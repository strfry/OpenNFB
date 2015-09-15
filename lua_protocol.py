
from PyQt5.QtCore import QUrl, QTimer, QFileSystemWatcher
from PyQt5.QtWidgets import *

from pyqtgraph.dockarea import *

import sys
import signal as _signal

from acquisition import UDPThread

import lupa
import flow

_signal.signal(_signal.SIGINT, _signal.SIG_DFL)
myApp = QApplication(sys.argv)


context = flow.Context()
context.register_channel('Channel 1')
context.register_channel('Channel 2')

analysisWindow = QMainWindow()

# Add channel global

def setup_lua(path):
	print ('Initializing Lua')
	global lua, guiBlocks
	lua = lupa.LuaRuntime()
	lua.globals()["flow"] = flow
	lua.globals()["channels"] = context.get_channels()
	source = open(path).read()
	lua.execute(source)

	guiBlocks = lua.eval('setup()')
	#lua.eval('gui()')

	area = DockArea()

	for block in guiBlocks:
		dock = Dock(block.name)
		dock.addWidget(block.widget())
		area.addDock(dock)

	analysisWindow.setCentralWidget(area)


path = 'protocols/test.lua'

setup_lua(path)
fileWatcher = QFileSystemWatcher()
fileWatcher.addPath(path)
fileWatcher.fileChanged.connect(lambda: setup_lua(path))

analysisWindow.show()

sourceThread = UDPThread()

def handlePacket(packet):
	context.append_channel_data('Channel 1', [packet[0]])
	context.append_channel_data('Channel 2', [packet[1]])
	context.process()

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()

def updateGUI():
	for block in guiBlocks:
		block.updateGUI()

guiTimer = QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)

myApp.exec_()
sys.exit()
