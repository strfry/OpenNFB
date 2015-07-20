from flow import Block
from flow.block import Input

from PySide import QtGui

class Oscilloscope(Block):
	def __init__(self, name, **config):
		super(Oscilloscope, self).__init__(**config)
		#self.define_input_array('channel', 4)

		self.channel = [Input(self, 'Channel %i' % x) for x in range(4)]

		self.define_config('autoscale', False)

	def widget(self):
		return QtGui.QWidget()

class Spectrograph(Block):
	def __init__(self, name, **config):
		super(Spectrograph, self).__init__(**config)

	def widget(self):
		return QtGui.QWidget()

class TextBox(Block):
	def __init__(self, name, **config):
		super(TextBox, self).__init__(**config)