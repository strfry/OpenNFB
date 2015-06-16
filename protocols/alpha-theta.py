from PySide import QtCore, QtGui
import pyqtgraph as pg
from transformations import FFT, GridFilter
from widgets import ScrollingPlot

gridFilter = GridFilter()
fftFilt = FFT()
rawPlot = ScrollingPlot()
alphaThetaPlot = ScrollingPlot()

rawPlot.plot('raw', pen='r')
#rawPlot.plot('dc', pen='b')
rawPlot.plot('ac', pen='g')

alphaThetaPlot.plot('alpha', pen='g')
alphaThetaPlot.plot('theta', pen='r')
#alphaThetaPlot.plot('alpha/theta', pen='y')

def widget():
    w = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    w.setLayout(layout)

    layout.addWidget(rawPlot, 0, 1)
    layout.addWidget(alphaThetaPlot, 1, 1)

    return w

foo = True
def update(channels):
    global foo
    gridFilter.update(channels[0])

    rawPlot.update('raw', channels[0])
    #rawPlot.update('dc', gridFilter.dc)
    #rawPlot.update('ac', gridFilter.ac)

    #fftFilt.update(gridFilter.ac)
    fftFilt.update(channels[0])
    alpha = fftFilt.bandPower(8, 12)
    theta = fftFilt.bandPower(4, 8)

    alphaThetaPlot.update('alpha', alpha)
    alphaThetaPlot.update('theta', theta)

    if theta == 0:
        theta = 1.0
    #alphaThetaPlot.update('alpha/theta', alpha/theta)

    #val = expit(np.log(float(alpha) / theta]))

def updateGUI():
    alphaThetaPlot.updateGUI()
    rawPlot.updateGUI()