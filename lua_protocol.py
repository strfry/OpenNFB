from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock

import sys
import signal as _signal

from acquisition import UDPThread
from launcher import LuaLauncher

import flow

_signal.signal(_signal.SIGINT, _signal.SIG_DFL)
myApp = QtGui.QApplication(sys.argv)


context = flow.Context()
context.register_channel('Channel 1')
context.register_channel('Channel 2')

analysisWindow = QtGui.QMainWindow()
area = DockArea()
analysisWindow.setCentralWidget(area)

path = 'protocols/test.lua'
if len(sys.argv) > 1:
	path = sys.argv[1]

launcher = LuaLauncher(context, path, area)

toolbar = QtGui.QToolBar()
saveAction = toolbar.addAction('Save Layout')
saveAction.triggered.connect(launcher.save_layout)
restoreAction = toolbar.addAction('Restore Layout')
restoreAction.triggered.connect(launcher.restore_layout)
analysisWindow.addToolBar(toolbar)

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


guiTimer = QtCore.QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)

myApp.exec_()
sys.exit()
