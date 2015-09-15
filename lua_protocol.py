
from PyQt5.QtCore import QUrl, QTimer, QFileSystemWatcher
from PyQt5.QtWidgets import QApplication, QMainWindow

from pyqtgraph.dockarea import DockArea, Dock

import sys
import signal as _signal

from acquisition import UDPThread
from launcher import LuaLauncher

import flow

_signal.signal(_signal.SIGINT, _signal.SIG_DFL)
myApp = QApplication(sys.argv)


context = flow.Context()
context.register_channel('Channel 1')
context.register_channel('Channel 2')

analysisWindow = QMainWindow()
area = DockArea()
analysisWindow.setCentralWidget(area)

path = 'protocols/test.lua'
if len(sys.argv) > 1:
	path = sys.argv[1]

launcher = LuaLauncher(context, path, area)

analysisWindow.show()

sourceThread = UDPThread()

def handlePacket(packet):
	context.append_channel_data('Channel 1', [packet[0]])
	context.append_channel_data('Channel 2', [packet[1]])
	context.process()

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()

def updateGUI():
	for block in launcher.guiBlocks:
		block.updateGUI()


guiTimer = QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)

myApp.exec_()
sys.exit()
