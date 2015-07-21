from flow import Block, Signal, Input

from PySide import QtGui
from pyqtgraph import PlotWidget

from traits.api import Bool, Instance

class Oscilloscope(Block):

	autoscale = Bool(False)
	channel0 = Input()
	channel1 = Input()

	def __init__(self, name, **config):
		super(Oscilloscope, self).__init__(**config)

		self._plot_widget = PlotWidget()
		self._plot_widget.block = self

		self.plot = self._plot_widget.plot()


	def widget(self):
		return self._plot_widget

	def updateGUI(self):
		self.plot.setData(self.channel0.buffer)
		pass

	def process(self):
		pass

class Spectrograph(Block):
	def __init__(self, name, **config):
		super(Spectrograph, self).__init__(**config)

	def widget(self):
		return QtGui.QWidget()

class TextBox(Block):
	def __init__(self, name, **config):
		super(TextBox, self).__init__(**config)