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
from rt_thread import set_realtime, thread_yield

class TestClock(QtCore.QThread):
	def __init__(self, sample_rate):
		super(TestClock, self).__init__()

		self.output = Signal()
		self.period = 1.0 / sample_rate

		#self.start(QtCore.QThread.HighestPriority)
		#self.start()
		threading.Thread(target=self.run).start()

	def clock_sample(self):
		self.output.append([monotonic()])
		self.output.process()

	def run(self):
		nperiod = int(self.period * 1000000000)
		ncomputation = nperiod // 10
		nconstraint = ncomputation * 2

		print (self.period, nperiod, ncomputation, nconstraint)

		set_realtime(nperiod, ncomputation, nconstraint)

		start = monotonic()
		while (True):
			loop_begin = monotonic()
			#print ('diff time %f' % (loop_begin - start))

			wait_time = start + self.period - monotonic()

			if wait_time <= 0.000001:
				start += self.period
				self.clock_sample()

				loop_end = monotonic()
				#print ('clock process took %f seconds' % (loop_end - loop_begin))
			elif wait_time > self.period / 2:
				#print ('%f seconds left, sleeping' % wait_time)
				thread_yield()

			else:
				pass

class JitterBuffer(Block):
	input = Input()

	buffer_size = 5

	def init(self, input, sample_rate):
		self.input = input
		self.output = Signal()
		self.period = 1.0 / sample_rate

		self.buffer = []

		self.started = False


	def process(self):
		newbuf = self.input.new
		newbuf.extend(self.buffer)
		self.buffer = newbuf

		if not self.started and len(self.buffer) > self.buffer_size:
			self.started = True

			import threading
			threading.Thread(target=self.run).start()

	def clock_sample(self):
		if len(self.buffer):
			self.output.append([self.buffer.pop()])
			self.output.process()
		else:
			print ('Warning: JitterBuffer ran empty')

	def run(self):
		nperiod = int(self.period * 1000000000)
		ncomputation = nperiod // 10
		nconstraint = ncomputation * 2

		print (self.period, nperiod, ncomputation, nconstraint)

		set_realtime(nperiod, ncomputation, nconstraint)

		start = monotonic()
		while (True):
			loop_begin = monotonic()
			#print ('diff time %f' % (loop_begin - start))

			wait_time = start + self.period - monotonic()

			if wait_time <= 0.000001:
				start += self.period
				self.clock_sample()

				loop_end = monotonic()
				#print ('clock process took %f seconds' % (loop_end - loop_begin))
			elif wait_time > self.period / 2:
				#print ('%f seconds left, sleeping' % wait_time)
				thread_yield()

			else:
				pass



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
		jitter = abs(diff - period) * 1000
		self.jitter.append([jitter])
		self.jitter.process()
