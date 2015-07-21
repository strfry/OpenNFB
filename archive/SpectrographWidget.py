from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
from transformations import IIRFilter

class SpectrographWidget(pg.PlotWidget):
    def __init__(self):
        super(SpectrographWidget, self).__init__()
        self.setLabel('bottom', 'Index', units='B')
        nPlots = 18
        nSamples = 500
        self.curves = []

        for i in range(nPlots):
            c = pg.PlotCurveItem(pen=(i, nPlots * 1.3))
            self.addItem(c)
            c.setPos(0, i * 6)
            self.curves.append(c)
            c.setData(np.zeros(nSamples))

        self.setYRange(0, nPlots * 6)
        self.setXRange(0, nSamples)

        self.buffer = np.zeros(nSamples)
        self.nPlots = nPlots

        self.filter = IIRFilter()


    def updateValue(self, newValue):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = newValue

        self.filter.update(newValue)

    def updateGUI(self):
        for i in range(self.nPlots):
            lo = float(i+0) / self.nPlots * 125.
            hi = float(i+1) / self.nPlots * 125.
            
            # Ugly workaround: Skip the bands containing 50 Hz and DC/Ultra Low Frequencies
            if i == 0 or (lo < 50 and hi > 50):
                print "pass", lo, hi
                continue

            foo = self.curves[i].getData()[1]
            foo[:-1] = foo[1:]
            foo[-1] = (self.filter.band(lo, hi) / 50)

            self.curves[i].setData(foo)
    
