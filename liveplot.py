from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import scipy.signal

from PySide import QtCore
from BDFReader import BDFReader
from SpectrogramWidget import SpectrogramWidget

import pyeeg
import sys

# QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
# mw = QtGui.QMainWindow()
# mw.resize(800,800)

win = pg.GraphicsWindow(title="Basic plotting examples")
# win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='y')
curve2 = p6.plot(pen='r')
data = np.zeros(1)
data2 = data
p6.setAutoPan(True)
p6.setXRange(0, 500)
p6.enableAutoRange('x', True)
p6.enableAutoRange('y', 0.8)

firHighPass = scipy.signal.firwin(199, 4.0, pass_zero=False, nyq=125.0)
firBandPass = scipy.signal.firwin(199, (4.0, 35.0), pass_zero=False, nyq=125.0)
iirBandPass = scipy.signal.iirfilter(17, [4.0 / 125., 35.0 / 125.], btype='band')

filter = firBandPass


@QtCore.Slot(object)
def handlePacket(packet):
    global curve, curve2, data, data2, p6, foo, filter

    data = np.append(data, packet[0])

    filterBuffer = data[-len(filter):]

    if not isinstance(filter[0], np.ndarray):
        # FIR Filter
        newValue = scipy.signal.lfilter(filter, [1.0], filterBuffer)[-1]
    else:
        # IIR Filter
        newValue = scipy.signal.lfilter(filter[1], filter[0], filterBuffer)[-1]

    data2 = np.append(data2, newValue)


    # curve.setData(data)
    curve2.setData(data2)

    power, ratios = pyeeg.bin_power(data2[-250:], [4, 8, 12, 15, 20, 30, 50], 250)
    foo.setOpts(height=ratios)


class BDFThread(QtCore.QThread):
    newPacket = QtCore.Signal(object)

    def __init__(self, filename):
        super(BDFThread, self).__init__()
        self.bdf = BDFReader(file(filename, 'rb'))

    def emitPacket(self):
        packet = self.bdf.readPacket()
        if packet:
            self.newPacket.emit(packet)
        else:
            self.quit()

    def run(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.emitPacket)
        timer.start(1000 / 250)

        self.exec_()


bdf = BDFThread(sys.argv[1])
bdf.newPacket.connect(handlePacket)
bdf.start()

win.nextRow()
p7 = win.addPlot(title='Frequency distribution')
foo = pg.BarGraphItem(x=range(6), height=range(6), width=0.5)
p7.addItem(foo)
p7.getAxis('bottom').setTicks([zip(range(6), ['Theta', 'Alpha', 'SMR', 'Beta', 'Hi Beta', 'Gamma'])])
foo.setOpts(brushes=[pg.hsvColor(x / 6.0) for x in range(6)])

win.nextRow()

#specPlot = win.addPlot(title='Spectrogram')
specWidget = SpectrogramWidget()
#win.addItem(specWidget)
#specPlot.addItem(specWidget)

def specgramHandler(packet):
    global specWidget
    specWidget.update(packet[0])

bdf.newPacket.connect(specgramHandler)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
