from flow import Block, Signal, Input

from traits.api import Range, Float, Int, on_trait_change, List, CFloat

import numpy as np
from scipy.signal import butter, lfilter, iirfilter

class BandPass(Block):
	input = Input()

	order = Range(low=2, high=8, value=5)
	lo = Float
	hi = Float
	nyquist = Float(125)

	def init(self, lo, hi, input):
		self.lo = lo
		self.hi = hi
		self.input = input
		self.output = Signal()

	@on_trait_change("lo,hi,order,nyquist")
	def _range_changed(self):
		b,a = iirfilter(self.order, (self.lo / self.nyquist, self.hi / self.nyquist))

		self._filter_b, self._filter_a = b,a

	def process(self):
		buffer = self.input.buffer[-self.order*3:]
		filt = lfilter(self._filter_b, self._filter_a, buffer)
		self.output.append(filt[-1:])
		self.output.process()


	@property
	def range(self):
		return self.lo, self.hi

### Simple Notch filter that works by delaying by half a period
class NotchDelay(Block):
	input = Input()

	frequency = Float(50.0)
	samplerate = Int(250)

	def init(self, input):
		self.readjust()
		self.input = input
		self.output = Signal()
		self.delayed = Signal()


	@on_trait_change("frequency,samplerate")
	def readjust(self):
		delay = self.samplerate / self.frequency / 2
		delay = 3
		self.delayline = [0] * int(delay) 

	def process(self):
		for sample in self.input.new:
			self.delayline[1:] = self.delayline[:-1]
			self.delayline[0] = sample
			self.output.append([self.delayline[-1] + sample])
			self.delayed.append([self.delayline[-1] + self.delayline[-2]])

		self.output.process()
		self.delayed.process()



class NotchFilter(Block):
	input = Input()

	frequency = Float(50.0)

	# Find out what module_pole is and rename it
	module_pole = Float(0.9)

	nyquist = Float(125.0)

	@on_trait_change("frequency,module_pole")
	def compute_filter(self):
		theta = 2 * np.pi * self.frequency / self.nyquist * 2
		zero = np.exp(np.array([1j, -1j]) * theta)
		pole = self.module_pole * zero

		self._filter_b = np.poly(zero)
		self._filter_a = np.poly(pole)


	def init(self, input):
		self.compute_filter()
		self.input = input

		self.output = Signal()



	def process(self):
		buffer = self.input.buffer
		assert self.input.new_samples == 1

		filt = lfilter(self._filter_b, self._filter_a, buffer)
		self.output.append(filt[-1:])
		self.output.process()


class DCBlock(Block):
	input = Input()

	def __init__(self, input, **config):
		self.dc = Signal()
		self.ac = Signal()

		super(DCBlock, self).__init__(**config)

		self.input = input

	def _input_changed(self):
		traits = self.input.trait_get(['label', 'color'])
		self.ac.trait_set(**traits)

	def process(self):
		for x in self.input.new:
			new_dc = self.dc.buffer[-1] * 0.95 + x * 0.05
			self.dc.append([new_dc])

		self.dc.process()


		self.ac.append([x - self.dc.buffer[-1] for x in self.input.new])
		self.ac.process()


class RMS(Block):
	input = Input()
	avg_size = Int(42)

	def init(self, input):
		self.output = Signal()
		self.input = input

	def _input_changed(self):
		self.output.copy_traits(self.input, ['label', 'color'])


	def process(self):
		buf = np.array(self.input.buffer[-self.avg_size:])
		rms = sum(buf ** 2) / len(buf)
		avg = np.sqrt(rms)

		self.output.append([avg])
		self.output.process()



class Averager(Block):
	input = Input()

	def __init__(self, input):
		self.output = Signal()
		self.average = 0.0
		self.factor = 0.99
		super(Averager, self).__init__(input=input)

	def process(self):
		for x in self.input.new:
			self.average = self.average * self.factor + x * (1.0 - self.factor)
			self.output.append([self.average])

		self.output.process()


class Trendline(Block):
	input = Input()
	interval = Int(25)

	def __init__(self, input):
		self.output = Signal(buffer_size=1000)
		self.cnt = 0

		super(Trendline, self).__init__(input=input)

	def _input_changed(self):
		traits = self.input.trait_get(['label', 'color'])
		self.ac.trait_set(**traits)

	def process(self):
		self.cnt += self.input.new_samples
		if self.cnt >= self.interval:
			self.cnt = 0

			avg = sum(self.input.buffer[-self.interval:]) / self.interval

			self.output.append([avg])
			self.output.process()


class Expression(Block):
	args = List(Input)
	input = Input()

	def init(self, func, *args):
		# HACK: should not directly reference lupa here
		import lupa
		if lupa.lua_type(args) == 'table':
			args = args.values()


		print ('Expression: ', func, args[0])
		self.func = func
		self.args = list(args)

		# Workaround for list event bug 
		self.input = args[0]

		self.output = Signal()

	def _input_changed(self):
		self.output.copy_traits(self.input, ['label', 'color'])

	def process(self):
		args = [chan.last for chan in self.args]
		self.output.append([self.func(*args)])
		self.output.process()

