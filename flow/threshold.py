from flow import Block, Input, Signal

from pyqtgraph import QtGui, QtCore

from traits.api import Float, Int, Enum, Bool
import numpy as np

class Threshold(Block):
	input = Input()

	average_period = Float(0.35)
	epoch = Float(30.0)

	auto_mode = Bool(True)
	mode = Enum('increase', 'decrease', 'range')

	auto_target = Float(90.)


	def init(self, name):

		self.epoch = 5.0

		self.FS = 250

		epoch_samples = int(self.FS * self.epoch)

		self.signal = Signal(buffer_size=epoch_samples)
		self.passfail = Signal()

		self.threshold = 1.0
		self.calc_cnt = 0

		self.bar = QtGui.QProgressBar(orientation=QtCore.Qt.Vertical)
		self.slider = QtGui.QSlider()

		self.slider.setRange(0, 100)

		self.pass_palette = self.bar.palette()

		if isinstance(self.input.color, QtGui.QColor):
			color = self.input.color
		else:
			color = QtGui.QColor(QtGui.qRgb(*self.input.color))
		
		self.pass_palette.setColor(QtGui.QPalette.Highlight, color)

		self.fail_palette = self.bar.palette()
		self.fail_palette.setColor(QtGui.QPalette.Highlight, QtCore.Qt.red)
		#self.fail_palette.setColor(self.bar.backgroundRole(), QtCore.Qt.red)

		self.bar.setPalette(self.fail_palette)
		self.bar.show()

		#self.bar.setStyleSheet("*{ background-color: rgb(45, 50, 30); }")


		
	def widget(self):
		w = QtGui.QWidget()
		l = QtGui.QHBoxLayout()
		l.addWidget(self.bar)
		l.addWidget(self.slider)

		w.setLayout(l)
		w.block = self

		return w

	def updateGUI(self):
		self.bar.setValue(self.signal.last)

		if self.passfail.last:
			self.bar.setPalette(self.pass_palette)
		else:
			self.bar.setPalette(self.fail_palette)

		if self.auto_mode:
			self.slider.setValue(self.threshold)

	def process(self):
		assert self.input.new_samples == 1

		avg_period_samples = int(self.average_period * self.FS)

		avg = sum(self.input.buffer[-avg_period_samples:]) / avg_period_samples
		self.signal.append([avg])
		self.signal.process()


		self.calc_cnt += 1
		if self.auto_mode and self.calc_cnt >= avg_period_samples:
			self.calc_cnt = 0

			self.threshold = np.percentile(self.signal.buffer, self.auto_target)

		success = False

		if self.mode == 'decrease':
			if avg < self.threshold:
				success = True
		elif self.mode == 'increase':
			if avg > self.threshold:
				success = True
		else:
			assert False, 'range Threshold not implemented'

		self.passfail.append([success])
		self.passfail.process()



