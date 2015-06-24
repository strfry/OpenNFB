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
alphaThetaPlot = ScrollingPlot()

rawPlot.plot('delta', pen=QtGui.QColor('violet'))
rawPlot.plot('theta', pen=QtGui.QColor('pink'))
rawPlot.plot('alpha', pen=QtGui.QColor('green'))
rawPlot.plot('smr', pen=QtGui.QColor('yellow'))
rawPlot.plot('beta', pen=QtGui.QColor('steelblue'))
#rawPlot.plot('highbeta', pen='b')

alphaThetaPlot.plot('alpha', pen='g')
alphaThetaPlot.plot('theta', pen='r')

trainingPlot = ScrollingPlot()
trainingPlot.plot('alpha/theta', pen='y')

spectrograph = SpectrographWidget()

def widget():
    w = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    w.setLayout(layout)

    layout.addWidget(rawPlot, 0, 0)
    layout.addWidget(alphaThetaPlot, 1, 0)
    layout.addWidget(trainingPlot, 2, 0)

    layout.addWidget(spectrograph, 0, 1, 0, 3)


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

iir0 = IIRFilter()
iir = IIRFilter()
iir2 = IIRFilter()
iir3 = IIRFilter()
iir4 = IIRFilter()

def update(channels):

    gridFilter.update(channels[0])

    iir0.update(channels[0])

    spectrograph.updateValue(channels[0])


    delta = iir.band(0.5, 4)
    sigWODelta = channels[0] - delta
    iir.update(sigWODelta)

    theta = iir.band(4, 8)
    sigWOTheta = sigWODelta - theta
    iir2.update(sigWOTheta)

    alpha = iir2.band(8, 12)
    sigWOAlpha = sigWOTheta - alpha
    iir3.update(sigWOAlpha)

    smr = iir3.band(12, 15)
    sigWOSMR = sigWOAlpha - smr
    iir4.update(sigWOSMR)

    beta = iir4.band(15, 25)
    sigWOAlpha = sigWOSMR - beta

    #rawPlot.update('delta', delta)
    #rawPlot.update('theta', theta)
    rawPlot.update('alpha', alpha)
    rawPlot.update('smr', smr)
    rawPlot.update('beta', beta)
#    rawPlot.update('alpha', iir.band(8, 12))
#    rawPlot.update('beta', iir.band(15, 20))
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
