from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import scipy.signal

from PySide import QtCore
from bdf import BDFReader, BDFWriter
from acquisition import BDFThread, OpenBCIThread

from SpectrogramWidget import SpectrogramWidget
import pyeeg
import sys

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Basic plotting examples")
#win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='y')
curve2 = p6.plot(pen='r')
data = np.zeros(1)
data2 = np.zeros(1)
data3 = np.zeros(1)
data4 = np.zeros(1)
p6.setAutoPan(True)
p6.setXRange(0, 500)
p6.enableAutoRange('x', True)
p6.enableAutoRange('y', 0.8)

class ViewBoxEndRanger:
  def __init__(self, viewBox):
    self.viewBox = viewBox
    viewBox.sigRangeChanged.connect(self.rangeChanged)
    viewBox.sigRangeChangedManually.connect(self.rangeChangedManually)
    viewBox.childrenChanged.connect(self.rangeChanged2)
    (xmin, xmax), _ = viewBox.viewRange()
    self.xwidth = xmax - xmin

  def rangeChanged2(self, foo):
    print "children changed", foo

  def rangeChanged(self, foo):
    (xmin, xmax), _ = self.viewBox.viewRange()
    xwidth = xmax-xmin
    (_, xmax), _ = self.viewBox.childrenBounds()
    p6.setRange(xRange=(xmax- xwidth*0.9, xmax + xwidth * 0.1), padding=0, update=False, disableAutoRange=False)

  def rangeChangedManually(self, _):
    self.viewBox.enableAutoRange('x', True)
    self.viewBox.enableAutoRange('y', 0.8)

vber = ViewBoxEndRanger(p6.getViewBox())
#p6.sigRangeChanged.connect(updateRange)
#p6.getViewBox().sigRangeChangedManually.connect(updateRangeManually)


firHighPass = scipy.signal.firwin(199, 4.0, pass_zero=False, nyq=125.0)
firBandPass = scipy.signal.firwin(199, (4.0, 35.0), pass_zero=False, nyq=125.0)
iirBandPass = scipy.signal.iirfilter(17, [4.0 / 125., 35.0 / 125.], btype='band')

filter = firBandPass


from mpd import MPDClient
client = MPDClient()  
client.connect("whisky", 6600)


def setMPDVolume(val):
  val = np.max(val, 0.3)
  client.setvol(int(val * 100))


win.nextRow()
p7 = win.addPlot(title="Updating plot")
curve3 = p7.plot(pen='g')

@QtCore.Slot(object)
def handlePacket(packet):
    global curve, curve2, data, data2, data3, data4, p6, p7, curve3, foo, filter

    #print '0', len(data)

    data = np.append(data,packet[0])

    #print '1', len(data)
		
    filterBuffer = data[-len(filter):]

    if not isinstance(filter[0], np.ndarray):
        # FIR Filter
        newValue = scipy.signal.lfilter(filter, [1.0], filterBuffer)[-1]
    else:
        # IIR Filter
        newValue = scipy.signal.lfilter(filter[1], filter[0], filterBuffer)[-1]

    data2 = np.append(data2, newValue)

    curve.setData(data4)
    curve2.setData(data2)

    #print '2', len(data)

    power, ratios = pyeeg.bin_power(data2[-250:], [4, 8, 12, 15, 20, 30, 50], 250)

    # Workaround to skip peaks at start:
    if len(data3) == 1000:
      data3 = [0] * 1000
    val = power[1] - power[0]
    data3 = np.append(data3, val)


    min_smr = np.min(data3[-5000:])
    max_smr = np.max(data3[-5000:])

    
#    val = (val - min_smr) /  (max_smr - min_smr)
    from scipy.special import expit
    if power[0] == 0.0: power[0] = 1.0
    val = expit(np.log(float(power[1]) / power[0]))


    if len(data3) % 30 == 0:
      data4 = np.append(data4,val)
      curve3.setData(data4)
      setMPDVolume(val)

    foo.setOpts(height=ratios)

    #print '3', len(data)

    #print data, data2, data3, data4

#sourceThread = BDFThread(sys.argv[1])
sourceThread = OpenBCIThread(sys.argv[1])

try:
  write_file = file(sys.argv[2], 'wb')
  import bdf
  writer = bdf.BDFWriter(8)
  sourceThread.newPacket.connect(writer.append_sample)
  QtGui.QApplication.instance().aboutToQuit.connect(lambda: writer.write_file(write_file))
except IndexError:
  print "No log file specified"
  pass

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()

win.nextRow()
p7 = win.addPlot(title='Frequency distribution')
foo = pg.BarGraphItem(x=range(6), height=range(6), width=0.5)
p7.addItem(foo)
p7.getAxis('bottom').setTicks([zip(range(6), ['Theta', 'Alpha', 'SMR', 'Beta', 'Hi Beta', 'Gamma'])])
foo.setOpts(brushes=[pg.hsvColor(x / 6.0) for x in range(6)])


win.nextRow()

##specPlot = win.addPlot(title='Spectrogram')
#specWidget = SpectrogramWidget()
#win.addItem(specWidget)
#specPlot.addItem(specWidget)

def specgramHandler(packet):
    global specWidget
    specWidget.update(packet[0])

#sourceThread.newPacket.connect(specgramHandler)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
       QtGui.QApplication.instance().exec_()

