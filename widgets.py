import pyqtgraph as pg
import numpy as np

class ScrollingPlot(pg.PlotWidget):
    def __init__(self, numSamples=1000, scrolling=True):
        super(ScrollingPlot, self).__init__()
        self.scrolling = True
        self.numSamples = numSamples
        self.plots = {}

        self.getPlotItem().setDownsampling(mode='peak')

    def plot(self, name, **kwargs):
        p = self.getPlotItem().plot(**kwargs)

        self.plots[name] = p
        p.buffer = np.zeros(self.numSamples)

        return p

    def update(self, name, newValue):
        # iF newValue is array, append [-1]
        p = self.plots[name]

        p.buffer[:-1] = p.buffer[1:]
        p.buffer[-1] = newValue

    def updateGUI(self):
        for p in self.plots.values():
            p.setData(p.buffer)



