
import lupa
import flow

from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock

class LuaLauncher(object):
	def __init__(self, context, path, dockarea):
		self.context = context
		self.path = path
		self.dockarea = dockarea

		self.watcher = QtCore.QFileSystemWatcher()
		self.watcher.addPath(path)
		self.watcher.fileChanged.connect(self.handle_reload)

		self.guiBlocks = []
		
		self.load_protocol(path)

	def load_protocol(self, path):
		lua = lupa.LuaRuntime()
		self.lua = lua
		lua.globals()["flow"] = flow
		lua.globals()["channels"] = self.context.get_channels()
		source = open(path).read()

		try:
			lua.execute(source)
			self.guiBlocks = lua.eval('setup()')
			#lua.eval('gui()')
		except Exception as e:
			print ('Lua Exception occured: ', e)

		for block in self.guiBlocks:
			dock = Dock(block.name)
			dock.addWidget(block.widget())
			self.dockarea.addDock(dock)

	def handle_reload(self):
		print(self.path, 'changed, reloading')

		# Delete all the stuff
		del self.lua

		for i in self.guiBlocks:
			del i.widget().block
		self.guiBlocks = ()

		self.context.clear_signals()

		# Weird pyqtgraph bug, need to clear twice to get them all
		self.dockarea.clear()
		self.dockarea.clear()

		# Reload protocol
		self.load_protocol(self.path)
