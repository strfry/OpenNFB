from block import Block, Input

import pyqtgraph as pg
import numpy as np

class Oscilloscope(Block):
    input = Input()

    def init(self, history=512, autoscale=True):
        self.widget = pg.PlotWidget()
        self.widget.block = self

        self.gr_block.set_history(history)

        self.plot = self.widget.plot()
        self.plot.setPen(QtGui.QColor(self.input.color))
        #self.widget.setYRange(*self.yrange)

        self.widget.enableAutoRange('y', 0.95 if autoscale else False)

        self.buffer = []

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateGUI)
        self.timer.start(100)


    def general_work(self, input_items, output_items):
        #print ('Oscilloscope work', len(input_items[0]), output_items, input_items[0][0])

        # TODO: Make relative to update rate
        self.gr_block.consume_each(5)

        self.buffer = input_items[0]

        return 0


    def updateGUI(self):
        self.plot.setData(self.buffer)
        self.widget.update()



class BarSpectrogram(Block):
    input = Input()


    def init(self, lo=0, hi=125, bins=256, yrange=750, ratio=False):
        self.widget = pg.PlotWidget()
        self.widget.setLabel('bottom', 'Frequency', units='Hz')

        self.bars = pg.BarGraphItem()

        self.win = np.hanning(bins)
        self.win = np.blackman(bins)
        #self.win = np.ones(bins)
        self.lo, self.hi = lo, hi
        self.ratio = ratio
        
        FS = self.input.sample_rate

        self.gr_block.set_history(bins)

        #num_bars = int(round((self.bins - 1) * (self.hi - self.lo) / FS))
        # This is total bullshit:
        num_bars = len(np.zeros(bins)[lo: hi])

        x = np.linspace(self.lo, self.hi, num_bars)

        self.bars = pg.BarGraphItem(x=x, height=range(num_bars), width=1.0)
        
        self.bars.setOpts(brushes=[pg.hsvColor(float(x) / num_bars) for x in range(num_bars)])
        self.widget.addItem(self.bars)

        # TODO: Better autoranging features
        #self.plot.enableAutoRange('xy', False)
        
        self.widget.setYRange(0, yrange)
        self.widget.enableAutoRange('y', 0.95)

        self.buffer = np.zeros(bins)

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateGUI)
        self.timer.start(10)


    def general_work(self, input_items, output_items):
        #print ('BarSpectrogram work', len(input_items[0]), output_items, input_items[0][0])

        self.gr_block.consume_each(16)

        self.buffer = input_items[0][-len(self.win):]
        return 0

    def updateGUI(self):


        C = np.fft.rfft(self.buffer * self.win)
        C = abs(C)

        lo, hi = self.lo, self.hi
        data = C[lo : hi]

        if self.ratio:
            data = data / sum(C)

        self.bars.setOpts(height=data)

        #self.widget.setData(input_items[0])
        self.widget.update()
        

    def widget(self):
        return self.plot
