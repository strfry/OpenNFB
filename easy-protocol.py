from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from transformations import FFT, GridFilter, IIRFilter
from widgets import ScrollingPlot
from SpectrographWidget import SpectrographWidget
from threshold import ThresholdWidget


class _(object):
    def __init__(self, device):
        self.device = device

        self.Cz = device.getChannel(0)
        
        self.alpha = BandPass(Cz, 8, 12)
        self.theta = BandPass(Cz, 4, 8)

    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        self.rawPlot = Oscilloscope()
        self.alphaThetaPlot = Oscilloscope()
        self.trainingPlot = Oscilloscope()

        self.threshold = ThresholdWidget()

        layout.addWidget(self.rawPlot, 0, 0)
        layout.addWidget(self.alphaThetaPlot, 1, 0)
        layout.addWidget(self.trainingPlot, 2, 0)

        return w


    def update(self):
        self.rawPlot.plot(Cz, pen=QColor('magenta'))
        
        self.trainingPlot.plot(alpha, pen=QColor('green'))
        self.trainingPlot.plot(theta, pen=QColor('red'))
        
        spectrograph(Cz)


a1 = Source('Channel 0')


SignalQuality('Channel 0')

bZ = a1 + c3

Fz = Signal()

win = Window()

filter = Filter('band', (13,42), type='elliptic')    \
    .in(bZ) \
    .out(Fz)
    .curve(Plot("Alpha filter response", xrange=()))

filter.curve = Plot('Alpha filter response', xrange=(), window=win)
