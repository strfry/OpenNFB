from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from scipy.special import expit
from transformations import FFT, GridFilter, IIRFilter
from widgets import ScrollingPlot

gridFilter = GridFilter()
fftFilt = FFT()
rawPlot = ScrollingPlot(1000)
alphaThetaPlot = ScrollingPlot()

rawPlot.plot('theta', pen='r')
rawPlot.plot('alpha', pen='g')
rawPlot.plot('beta', pen='b')
#rawPlot.plot('highbeta', pen='b')

alphaThetaPlot.plot('alpha', pen='g')
alphaThetaPlot.plot('theta', pen='r')

trainingPlot = ScrollingPlot()
trainingPlot.plot('alpha/theta', pen='y')

def widget():
    w = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    w.setLayout(layout)

    layout.addWidget(rawPlot, 0, 2)
    layout.addWidget(alphaThetaPlot, 1, 2)
    layout.addWidget(trainingPlot, 2, 2)


    return w

def setMPDVolume(_): pass

try:
  from mpd import MPDClient
  client = MPDClient()
  client.connect("localhost", 6600)

  def setMPDVolume(val):
    val = 100 - val
    val = np.min((np.max((val, 10)), 100))
    client.setvol(int(val))
except Exception, e:
  print "MPD error: ", e

iir = IIRFilter()

def update(channels):
    gridFilter.update(channels[0])

    iir.update(channels[0])
    rawPlot.update('theta', iir.band(4, 8))
    rawPlot.update('alpha', iir.band(8, 12))
    rawPlot.update('beta', iir.band(15, 20))
    #rawPlot.update('highbeta', iir.band(15, 25))

    #rawPlot.update('dc', gridFilter.dc)
    #rawPlot.update('ac', gridFilter.ac)

    #fftFilt.update(gridFilter.ac)
    fftFilt.update(gridFilter.ac)
    alpha = fftFilt.bandPower(8, 12)
    theta = fftFilt.bandPower(4, 8)
    #rawPlot.update('raw', fftFilt.bandPower(1, 30))

    alphaThetaPlot.update('alpha', alpha)
    alphaThetaPlot.update('theta', theta)

    if theta == 0:
        theta = 1.0
    trainingValue = np.log(alpha/theta)
    trainingValue = expit(np.log(float(alpha) / theta))
    trainingPlot.update('alpha/theta', trainingValue)

    setMPDVolume(trainingValue * 70)

def updateGUI():
    alphaThetaPlot.updateGUI()
    rawPlot.updateGUI()
    trainingPlot.updateGUI()
