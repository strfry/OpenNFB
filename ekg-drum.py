from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from scipy.special import expit
from transformations import FFT, GridFilter, IIRFilter
from widgets import ScrollingPlot
from SpectrographWidget import SpectrographWidget

gridFilter = GridFilter()
fftFilt = FFT()
rawPlot = ScrollingPlot(1000)

rawPlot.plot('raw', pen=QtGui.QColor('red'))

filteredPlot = ScrollingPlot()
filteredPlot.plot('ac', pen='r')
filteredPlot.plot('abs', pen='g')

heartbeatPlot = ScrollingPlot()
heartbeatPlot.plot('ekg', pen=QtGui.QColor('green'))
heartbeatPlot.plot('percentile', pen=QtGui.QColor('violet'))
heartbeatPlot.plot('beat', pen=QtGui.QColor('red'))


def widget():
    w = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    w.setLayout(layout)

    layout.addWidget(rawPlot, 0, 0)
    layout.addWidget(filteredPlot, 1, 0)
    layout.addWidget(heartbeatPlot, 3, 0)

    return w

import rtmidi2

class Heartbeat(object):
    def __init__(self, window=500):
        self.out = 0
        self.buffer = np.zeros(window)
        self.threshold = 0.0
        self.lastBeat = 0

        self.sound = QtGui.QSound('drum.wav')

        self.midi_out = rtmidi2.MidiOut()
        # open the first available port
        self.midi_out.open_port(0)
        # send C3 with vel. 100 on channel 1
        pass

    def process(self, newValue):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = newValue

        self.threshold = np.percentile(self.buffer, 98)

        beat = 10000.0 if newValue > self.threshold else 0.0

        self.lastBeat += 1

        if beat > 0 and self.lastBeat > 50:
            self.lastBeat = 0
            self.beat = 10000.0
            #self.sound.play()
            print "beat event"
            self.midi_out.send_noteon(0, 48, 100)
        else:
            self.beat = 0.0



hb = Heartbeat()

def update(channels):
    rawPlot.update('raw', channels[0])

    gridFilter.update(channels[0])

    filteredPlot.update('ac', gridFilter.ac)
    filteredPlot.update('abs', abs(gridFilter.ac))

    hb.process(abs(gridFilter.ac))
    heartbeatPlot.update('ekg', hb.buffer[-1])
    heartbeatPlot.update('percentile', hb.threshold)


    heartbeatPlot.update('beat', hb.beat)





def updateGUI():
    rawPlot.updateGUI()
    filteredPlot.updateGUI()
    heartbeatPlot.updateGUI()
