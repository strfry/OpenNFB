import importlib
import imp

from PySide import QtCore, QtGui

class ProtocolLauncher(object):
	def __init__(self, context, path):
		self.context = context
		self.path = path
		self.win = QtGui.QMainWindow()

		self.watcher = QtCore.QFileSystemWatcher()
		self.watcher.addPath(path)
		self.watcher.fileChanged.connect(self.on_file_changed)

		self.holdoff = QtCore.QTimer()
		self.holdoff.setSingleShot(True)
		self.holdoff.timeout.connect(self.handle_reload)
		
		self.load_protocol(path)

	def load_protocol(self, path):
	    self.protocol = imp.load_module('protocol', file(path), path, ('.py', 'U', 1))
	    self.flow = self.protocol.flow()

	    self.flow.init(self.context)
	    self.widget = self.flow.widget()
	    self.win.setCentralWidget(self.widget)
	    self.win.show()

	def on_file_changed(self):
		# Implement a hold-off timer, since the callback is often called several times

		self.holdoff.start(2500)

	def handle_reload(self):
		print self.path, 'changed, reloading'

		del self.flow
		del self.protocol
		# Delete all the stuff

		self.context.clear_signals()

		self.load_protocol(self.path)
		# Reload protocol
		pass