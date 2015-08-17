
from flow import Block, Signal, Input

from pyqtgraph import QtGui
import pyqtgraph as pg
import numpy as np

from traits.api import Bool, List, on_trait_change, Int, Float, CFloat, Enum, Trait

class Oscilloscope(Block):

	autoscale = Bool(True)
	channels = List(Input())

	def __init__(self, name, **config):
		self._plot_widget = pg.PlotWidget(title=name)
		self._plot_widget.block = self

		self.plots = {}

		self._autoscale_changed()

		super(Oscilloscope, self).__init__(**config)


	@on_trait_change('channels[]')
	def channels_changed(self, object, name, old, new):
		for channel in old:
			del self.plots[channel]
		for channel in new:
			plot = self._plot_widget.plot()
			
			if isinstance(channel.color, QtGui.QColor):
				color = channel.color
			else:
				color = QtGui.qRgb(*channel.color)
			
			plot.setPen(QtGui.QColor(color))
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

    def init(self, name):
        self.plot = pg.PlotWidget(title=name)
        self.plot.block = self

        self.plot.setLabel('bottom', 'Frequency', units='Hz')

        self.bars = pg.BarGraphItem()

        self.setup_range()
        self.plot.addItem(self.bars)

        # TODO: Better autoranging features
        #self.plot.enableAutoRange('xy', False)
        
        self.plot.setYRange(0, self.yrange)

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
