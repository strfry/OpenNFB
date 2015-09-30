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
context.register_channel(0, 'Channel 1')
context.register_channel(1, 'Channel 2')

sourceThread = UDPThread()

def handlePacket(packet):
	context.append_channel_data(0, [packet[0]])
	context.append_channel_data(1, [packet[1]])
	context.process()

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()

class LauncherWindow(QtGui.QMainWindow):
	def __init__(self, context):
		super(LauncherWindow, self).__init__()
		self.context = context
		self.launcher = None

		self.dockarea = DockArea()
		self.setCentralWidget(self.dockarea)

		toolbar = QtGui.QToolBar()

		openIcon = self.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon)
		openAction = toolbar.addAction(openIcon, 'Load Protocol')
		openAction.triggered.connect(self.open_dialog)

		saveAction = toolbar.addAction('Save Layout')
		saveAction.triggered.connect(self.save_layout)
		restoreAction = toolbar.addAction('Restore Layout')
		restoreAction.triggered.connect(self.restore_layout)
		self.addToolBar(toolbar)

		self.guiTimer = QtCore.QTimer(self)
		#self.guiTimer.setSingleShot(True)
		self.guiTimer.timeout.connect(self.updateGUI)
		self.guiTimer.start(0)

	def save_layout(self):
		if self.launcher:
			self.launcher.save_layout()

	def restore_layout(self):
		if self.launcher:
			self.launcher.restore_layout()

	def load_protocol(self, path):
		self.launcher = LuaLauncher(self.context, path, self.dockarea)

	def open_dialog(self):
		filename, extension = QtGui.QFileDialog.getOpenFileName(self, directory='protocols', filter='*.lua')
		if filename:
			self.load_protocol(filename)


	def updateGUI(self):
		if self.launcher:
			for block in self.launcher.guiBlocks:
				block.updateGUI()


mainWindow = LauncherWindow(context)

if len(sys.argv) > 1:
	path = sys.argv[1]
	mainWindow.load_protocol(path)

mainWindow.show()

myApp.exec_()
sys.exit()
