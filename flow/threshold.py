from flow import Block, Input, Signal

from pyqtgraph import QtGui, QtCore

from traits.api import Float, Int, Enum, Bool
import numpy as np

class ThresholdWidget(QtGui.QWidget):
	MAX = 1000

	def __init__(self, threshold):
		QtGui.QWidget.__init__(self)

		self.threshold = threshold

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)

		width = self.width()
		height = self.height()

		top, bottom = height * .1, height * .8
		left, right = width * .1, width * .8

		rect = QtCore.QRect(left, top, right, bottom)		
		painter.fillRect(rect, QtGui.QColor('black'))

		#painter.setWindow(rect)

		dist = bottom - top

		relval = self.threshold.signal.buffer[-1] / self.MAX
		relval = min(1.0, relval)

		reltop = (1.0 - relval) * bottom + top
		relbottom = height * 0.9 - reltop 

		rect = QtCore.QRect(left, reltop, right, relbottom)

		color = QtGui.QColor('green' if self.threshold.passfail.buffer[-1] else 'red')
		painter.fillRect(rect, color)


		thr_height = self.threshold.threshold / self.MAX

		thr_top = (1.0 - thr_height) * bottom + top

		rect = QtCore.QRect(left, thr_top, right, 2)		
		painter.fillRect(rect, QtGui.QColor('white'))


		#painter.setBrush

class Threshold(Block):
	input = Input()

	average_period = Float(0.35)
	epoch = Float(3.0)

	auto_mode = Bool(True)
	mode = Enum('increase', 'decrease', 'range')

	auto_target = Float(0.90)

	low_target = Float(0.90)
	high_target = Float(0.90)


	def init(self, name, input):
		self.FS = 250
		self.name=name

		epoch_samples = int(self.FS * self.epoch)

		self.signal = Signal(buffer_size=epoch_samples)
		self.passfail = Signal()
		self.ratio = Signal()

		self.threshold = 1.0
		self.high_threshold = 0.0

		self.calc_cnt = 0

		self.bar = QtGui.QProgressBar(orientation=QtCore.Qt.Vertical)
		self.slider = QtGui.QSlider()

		self.slider.setRange(0, 17)
		self.bar.setRange(0, 17)

		self.pass_palette = self.bar.palette()

		self.input = input

		if isinstance(self.input.color, QtGui.QColor):
			self.color = self.input.color
		else:
			self.color = QtGui.QColor(self.input.color)


		self.bar.setStyleSheet("""
			QProgressBar::chunk { background: red; }
			QProgressBar::chunk[pass='true'] { background: %s ; }
			""" % self.color.name())


		self.button = QtGui.QPushButton("config")
		self.button.clicked.connect(self.configure_traits)

		self._widget = ThresholdWidget(self)

	def widget(self):
		return self._widget

		w = QtGui.QGroupBox()
		w.setTitle(self.name)

		l = QtGui.QGridLayout()
		l.addWidget(self.bar, 0, 0)
		l.addWidget(self.slider, 0, 1)

		l.addWidget(self.button, 1, 0, 1, 2)

		w.setLayout(l)
		w.block = self

		return w

	def updateGUI(self):
		self._widget.update()
		return
		self.bar.setValue(self.signal.last)

		self.bar.setProperty('pass', self.passfail.last)
		self.bar.style().polish(self.bar)
		
		if self.auto_mode:
			self.slider.setValue(self.threshold)

			#print type(self.threshold), self.threshold, self.nameano

	def process(self):
		assert self.input.new_samples == 1

		avg_period_samples = int(self.average_period * self.FS)

		avg = sum(self.input.buffer[-avg_period_samples:]) / avg_period_samples
		self.signal.append([avg])
		self.signal.process()



		self.calc_cnt += 1
		if self.auto_mode and self.calc_cnt >= avg_period_samples:
			self.calc_cnt = 0

			if self.mode == 'decrease':
				self.threshold = np.percentile(self.signal.buffer, 100 * self.auto_target)
			elif self.mode == 'increase':
				self.threshold = np.percentile(self.signal.buffer, 100 - 100 * self.auto_target)
			else:
				self.high_threshold = np.percentile(self.signal.buffer, self.high_target)
				self.threshold = np.percentile(self.signal.buffer, 100 - 100 * self.low_target)

		success = False

		self.ratio.append([avg / self.threshold])
		self.ratio.process()

		if self.mode == 'decrease':
			if avg < self.threshold:
				success = True
		elif self.mode == 'increase':
			if avg > self.threshold:
				success = True
		else:
			if avg > self.threshold and avg < self.high_threshold:
				success = True

		self.passfail.append([float(success)])
		self.passfail.process()



