#!/usr/bin/env python

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import scipy.signal

from bdf import BDFReader, BDFWriter
from acquisition import BDFThread, OpenBCIThread

import sys, imp

from flow import Context

app = QtGui.QApplication(sys.argv)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

protocol_name = sys.argv[1]
replay_file = sys.argv[2]

from protocols import ProtocolLauncher

context = Context()
context.register_channel('Channel 1')
context.register_channel('Channel 2')

launcher = ProtocolLauncher(context, protocol_name)

sourceThread = BDFThread(sys.argv[2])

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

#win = QtGui.QMainWindow()
#win.setWindowTitle("OpenNFB")
#win.resize(800, 600)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
       QtGui.QApplication.instance().exec_()

