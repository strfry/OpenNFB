from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import scipy.signal

from PySide import QtCore
from bdf import BDFReader, BDFWriter
from acquisition import BDFThread, OpenBCIThread, UDPThread

import sys, imp

from flow import Context

app = QtGui.QApplication.instance()
if not app:
    app = QtGui.QApplication(sys.argv)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

protocol_name = sys.argv[1]

from protocols import ProtocolLauncher

context = Context()
context.register_channel('Channel 1')
context.register_channel('Channel 2')

launcher = ProtocolLauncher(context, protocol_name)

#sourceThread = BDFThread(sys.argv[2])
#sourceThread = OpenBCIThread(sys.argv[2])
sourceThread = UDPThread()


def handlePacket(packet):
    context.append_channel_data('Channel 1', [packet[0]])
    context.append_channel_data('Channel 2', [packet[1]])
    context.process()

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()


def updateGUI():
    for child in launcher.widget.children():
        if hasattr(child, 'block'):
            child.block.updateGUI()

guiTimer = QtCore.QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)


try:
    write_file = file(sys.argv[2], 'wb')
    import bdf
    writer = bdf.BDFWriter(8)
    sourceThread.newPacket.connect(writer.append_sample)
    QtGui.QApplication.instance().aboutToQuit.connect(lambda: writer.write_file(write_file))
except IndexError:
  print "No log file specified"


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
       QtGui.QApplication.instance().exec_()

