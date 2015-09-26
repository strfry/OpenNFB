from flow import Block, Input, Signal

from time import monotonic
import numpy as np

from pyqtgraph import QtCore


def moving_average_exp(alpha, data):
	assert 0.0 < alpha < 1.0

	lower_threshold = 1e-2

	#window_size = int(np.ceil(np.log(lower_threshold) / np.log(alpha)))
	window_size = len(data)

	window = [alpha ** i for i in range(window_size)]
	window.reverse()
	window = np.array(window)

	s = np.sum(window)

	return np.sum(window * data[-window_size:]) / s

import threading

class TestClock(QtCore.QThread):
	def __init__(self, sample_rate):
		super(TestClock, self).__init__()

		self.output = Signal()

		#self.timer = QtCore.QTimer()
		#self.timer.timeout.connect(self.clock_sample)
		#self.timer.start(10.1 / sample_rate)

		self.period = 1.0 / sample_rate

		#self.thread = threading.Thread(target=self.clock_sample)
		#self.thread.run()

		print ('TestClock init')
		#self.start(QtCore.QThread.HighestPriority)
		self.start()

	def clock_sample(self):
		self.output.append([monotonic()])
		self.output.process()

	def run(self):
		start = monotonic()
		while (True):
			if monotonic() >= start + self.period:
				#print ('sample', start, monotonic())
				start += self.period
				self.clock_sample()



class ClockAnalyzer(Block):
	input = Input()
	alpha = 0.5

	def init(self, input):
		self.input = input
		self.last_time = monotonic()

		self.time_diff = Signal()
		self.sample_rate = Signal()
		self.jitter = Signal()

	def process(self):
		#self.input.buffer_size = 1024

		#if len(self.input.buffer) < 1024: return

		new_time = monotonic()
		diff = new_time - self.last_time
		self.last_time = new_time

		self.time_diff.append([diff])
		self.time_diff.process()

		sample_rate = 1.0 / moving_average_exp(self.alpha, self.time_diff.buffer)

		self.sample_rate.append([sample_rate])
		self.sample_rate.process()

		period = 1.0 / sample_rate
		jitter = abs(diff - period)
		self.jitter.append([jitter])
		self.jitter.process()
