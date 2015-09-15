
from flow import Block, Signal, Input

import pyqtgraph as pg
from pyqtgraph import QtGui
import numpy as np

from traits.api import Bool, List, on_trait_change, Int, Float, CFloat, Enum, Trait, Str

class Oscilloscope(Block):

    autoscale = Bool(True)
    channels = List(Input())
    name = Str()

    def __init__(self, name, channels, **config):
        self._plot_widget = pg.PlotWidget(title=name)
        self._plot_widget.block = self

        self.plots = {}

        self._autoscale_changed()

        self.name = name

        # Workaround for lua tables
        if hasattr(channels, 'values'):
            channels = channels.values()
        channels = list(channels)

        super(Oscilloscope, self).__init__(channels=channels, **config)

    @on_trait_change('channels[]')
    def channels_changed(self, object, name, old, new):
        for channel in old:
            del self.plots[channel]
        for channel in new:
            plot = self._plot_widget.plot()
            
            
            plot.setPen(QtGui.QColor(channel.color))
            self.plots[channel] = plot

    def _autoscale_changed(self):
        self._plot_widget.enableAutoRange('y', 0.95 if self.autoscale else False)


    def widget(self):
        return self._plot_widget

    def updateGUI(self):
        for channel in self.plots:
            plot = self.plots[channel]
            plot.setData(channel.buffer)

    def process(self):
        pass

class Spectrograph(Block):
    CHUNKSZ = Int(256)
    input = Input()
        
    def __init__(self, name, **config):
        self.img = pg.ImageItem()
        self.plot_widget = pg.PlotWidget(title=name)
        self.plot_widget.block = self

        self.plot_widget.addItem(self.img)

        #self.img_array = np.zeros((1000, self.CHUNKSZ/2+1))
        self.img_array = np.zeros((1000, 48))

        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)
        self.img.setLevels([-2,7])

        FS = 48 * 2

        freq = np.arange((self.CHUNKSZ/2)+1)/(float(self.CHUNKSZ)/FS)
        yscale = 1.0/(self.img_array.shape[1]/freq[-1])
        self.img.scale((1./FS)*self.CHUNKSZ, yscale)

        self.plot_widget.setLabel('left', 'Frequency', units='Hz')

        self.win = np.hanning(self.CHUNKSZ)
        #self.show()
        super(Spectrograph, self).__init__(**config)
        
    def process(self):
        # normalized, windowed frequencies in data chunk
        spec = np.fft.rfft(self.input.buffer*self.win) / self.CHUNKSZ

        spec = spec[0:48]
        # get magnitude 
        psd = abs(spec)
        # convert to dB scale
        psd = np.log10(psd)
        
        #self.img.setLevels([min(psd), max(psd)])
        
        #print (psd)

        # roll down one and replace leading edge with new data
        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = psd

        self.img.setImage(self.img_array, autoLevels=False)

    def widget(self):
        return self.plot_widget
        
    def updateGUI(self):
        pass

class TextBox(Block):
    def __init__(self, name, **config):
        super(TextBox, self).__init__(**config)


class BarSpectrogram(Block):
    input = Input()

    bins = Int(256)
    lo, hi = CFloat(1), CFloat(30)
    align = Trait('bottom', Enum('left', 'right', 'top', 'bottom'))

    yrange = Int(65000)

    ratio = Bool(False)
    sampling_rate = Float(250)

    def init(self, name, input):
        self.plot = pg.PlotWidget(title=name)
        self.plot.block = self

        self.plot.setLabel('bottom', 'Frequency', units='Hz')

        self.bars = pg.BarGraphItem()

        self.setup_range()
        self.plot.addItem(self.bars)

        # TODO: Better autoranging features
        #self.plot.enableAutoRange('xy', False)
        
        self.plot.setYRange(0, self.yrange)

        self.input = input
        self.name = name

    @on_trait_change('bins,lo,hi')
    def setup_range(self):
        self.win = np.hanning(self.bins)
        
        FS = self.sampling_rate

        #num_bars = int(round((self.bins - 1) * (self.hi - self.lo) / FS))
        num_bars = len(np.zeros(self.bins)[self.lo: self.hi])

        #print 'num_bars', num_bars, self.bins * (self.hi - self.lo) / FS

        x = np.linspace(self.lo, self.hi, num_bars)

        self.bars = pg.BarGraphItem(x=x, height=range(num_bars), width=1.0)
        
        self.bars.setOpts(brushes=[pg.hsvColor(float(x) / num_bars) for x in range(num_bars)])

    def process(self):
        pass

    def updateGUI(self):

        C = np.fft.rfft(self.input.buffer[-self.bins:] * self.win)
        C = abs(C)

        lo, hi = self.lo, self.hi
        data = C[lo : hi]

        if self.ratio:
            data = data / sum(C)

        self.bars.setOpts(height=data)
        

    def widget(self):
        return self.plot



class Waterfall(Block):
    input = Input()

    history_size = 100

    window_size = Int(512)
    lo, hi = CFloat(1), CFloat(30)
    #align = Trait('bottom', Enum('left', 'right', 'top', 'bottom'))

    logarithm = Bool(False)
    sampling_rate = Float(250)

    update_rate = 20

    def init(self, name):
        self.autoscale_button = QtGui.QCheckBox('Autoscale')
        self.autoscale_button.setCheckState(True)

        self.plot_widget = pg.PlotWidget(title=name)
        self.plot_widget.block = self

        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.setLabel("left", "Time", units='s')

        #TODO: listener for this
        #self.plot_widget.setYRange(-self.history_size / self.sampling_rate, 0)

        #self.plot_widget.setLimits(xMin=0, yMax=0)
        #self.plot_widget.showButtons()
        #self.waterfallPlotWidget.setAspectLocked(True)
        #self.waterfallPlotWidget.setDownsampling(mode="peak")
        #self.waterfallPlotWidget.setClipToView(True)
        
        # Setup histogram widget (for controlling waterfall plot levels and gradients)
        self.histogram = pg.PlotWidget(title='Histogram')
        self.waterfallHistogram = pg.HistogramLUTItem()
        self.histogram.addItem(self.waterfallHistogram)
        self.waterfallHistogram.gradient.loadPreset("flame")
        #self.waterfallHistogram.setHistogramRange(-50, 0)
        #self.waterfallHistogram.setLevels(-50, 0)

        self.waterfallImg = pg.ImageItem()
        self.plot_widget.clear()
        self.plot_widget.addItem(self.waterfallImg)      
        self.waterfallHistogram.setImageItem(self.waterfallImg)

        self.setup_range()

        self.update_counter = 0

    @on_trait_change('window_size,input')
    def size_input(self):
        if self.input.buffer_size < self.window_size:
            self.input.buffer_size = self.window_size
        
    @on_trait_change('window_size,lo,hi,history_size,sampling_rate,update_rate')
    def setup_range(self):

        self.window = np.hanning(self.window_size)

        nyquist = self.sampling_rate / 2

        bins = self.window_size / 2 + 1

        freqs = np.linspace(0, nyquist, bins)

        freq_step = nyquist / bins

        # Calculate bin indices
        self.lo_index = int(np.floor(self.lo / freq_step))
        self.hi_index = int(np.ceil(self.hi / freq_step))

        # Snap values to actual bin frequencies
        self.lo = freq_step * self.lo_index
        self.hi = freq_step * self.hi_index

        display_bins = self.hi_index - self.lo_index

        self.waterfallImgArray = np.zeros((self.history_size, display_bins))

        history_time = self.history_size / self.sampling_rate * self.update_rate
        self.waterfallImg.resetTransform()
        self.waterfallImg.setPos(self.lo, -history_time)
        self.waterfallImg.scale((self.hi - self.lo) / display_bins, history_time / self.history_size)
        #self.plot_widget.setYRange(-self.history_size / self.sampling_rate, 0)


    def process(self):
        self.update_counter += 1
        if self.update_counter == self.update_rate:
            self.update_counter = 0
        else:
            return

        C = np.fft.rfft(self.input.buffer[-self.window_size:] * self.window)
        C = abs(C)
        C = C[self.lo_index: self.hi_index]

        if self.logarithm:
            C = np.log(C)

        # Roll down one and replace leading edge with new data
        self.waterfallImgArray = np.roll(self.waterfallImgArray, -1, axis=0)
        self.waterfallImgArray[-1] = C

    def updateGUI(self):
        self.waterfallImg.setImage(self.waterfallImgArray.T,
                                   autoLevels=self.autoscale_button.checkState(),
                                   #autoRange=False
                                   )


    # TODO: This is overwritten by widget member
    def widget(self):
        config_widget = QtGui.QWidget()

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.autoscale_button)
#        layout.addWidget(self.histogram)

        config_widget.setLayout(layout)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(config_widget)

        main_widget = QtGui.QWidget()
        main_widget.setLayout(layout)
        main_widget.block = self

        return main_widget





