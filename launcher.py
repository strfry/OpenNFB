
import lupa
import flow
import sys

from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock

def to_lua(obj):
	if isinstance(obj, dict):
		content = [str(key) + ' = ' + to_lua(obj[key]) for key in obj]
		return "{ " + ", ".join(content) + "}"
	elif isinstance(obj, (tuple, list)):
		content = [to_lua(item) for item in obj]
		return "{ " + ", ".join(content) + "}"
	elif isinstance(obj, (str, int)):
		return repr(obj)
	elif isinstance(obj, unicode):
		return repr(str(obj))
	else:
		raise Exception('to_lua: Unknown type ' + str(type(obj)))

def to_python(obj):
	if isinstance(obj, str):
		return str(obj)
	elif sys.version_info.major < 3:
		if isinstance(obj, unicode):
			return str(obj)
	if isinstance(obj, int):
		return obj
	# Ugly Hack: If index 1 exists, we heuristically assume the table was a list/tuple once
	elif 1 in obj:
		return [to_python(item) for item in obj.values()]
	# Assume dict table
	else:
		return {str(key): to_python(obj[key]) for key in obj}

def getter(obj, attr_name):
	#print ('getter', obj, attr_name)

	if isinstance(attr_name, int):
		return obj[attr_name]
	else:
		return getattr(obj, attr_name)

def setter(obj, attr_name, value):
	#print ('setter', obj, attr_name, value)

	attr = getattr(obj, attr_name)

	if isinstance(attr_name, int):
		obj[attr_name] = value
	elif isinstance(attr, str):
		setattr(obj, attr_name, value)		
	elif hasattr(attr, '__item__') or hasattr(attr, '__getitem__'):
		setattr(obj, attr_name, tuple(value.values()))
	else:
		setattr(obj, attr_name, value)

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
		lua = lupa.LuaRuntime(attribute_handlers=(getter, setter))
		self.lua = lua
		lua.globals()["flow"] = flow
		lua.globals()["channels"] = self.context.get_channels()
		source = open(path).read()

		try:
			lua.execute(source)
			self.guiBlocks = lua.eval('setup()')
			#lua.eval('gui()')
		except Exception as e:
			print ('Lua Exception occured: ', e, type(e))
			raise

		for block in self.guiBlocks:
			dock = Dock(block.name)
			dock.addWidget(block.widget())
			self.dockarea.addDock(dock)

		if 'doc_config' in lua.globals():
			self.restore_layout()


	def handle_reload(self):
		print(self.path, 'changed, reloading')

		# Delete all the stuff
		del self.lua

		for i in self.guiBlocks:
			if hasattr(i, 'block'):
				del i.widget().block
		self.guiBlocks = ()

		self.context.clear_signals()

		# Weird pyqtgraph bug, need to clear the DockArea twice to remove all components
		self.dockarea.clear()
		self.dockarea.clear()

		# Reload protocol
		self.load_protocol(self.path)

	config_marker = '\n\n' + '-' * 23 + "Auto-Generated config - DO NOT EDIT" + "-" * 23

	def save_layout(self):
		save = to_lua(self.dockarea.saveState())

		source = open(self.path).read()

		# Throw away auto-generated part
		source = source.split(self.config_marker)[0]

		writer = open(self.path, 'w')
		writer.write(source)
		writer.write(self.config_marker)
		writer.write('\nfunction doc_config()\n\treturn ')
		writer.write(save)
		writer.write('\nend')
		writer.close()

	def restore_layout(self):
		state = to_python(self.lua.eval('doc_config()'))
		self.dockarea.restoreState(state)

