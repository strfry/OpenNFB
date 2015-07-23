from flow import Block, Signal, Input

from traits.api import Range, Float, on_trait_change

from scipy.signal import butter, lfilter, iirfilter

class BandPass(Block):
	input = Input()

	order = Range(low=2, high=8, value=5)
	lo = Float
	hi = Float
	nyquist = Float(125)

	def __init__(self, lo, hi, **config):
		super(BandPass, self).__init__(lo=lo, hi=hi, **config)

		self.output = Signal()

	@on_trait_change("lo,hi,order,nyquist")
	def _range_changed(self):
		b,a = iirfilter(self.order, (self.lo / self.nyquist, self.hi / self.nyquist))

		self._filter_b, self._filter_a = b,a

	def process(self):
		buffer = self.input.buffer
		filt = lfilter(self._filter_b, self._filter_a, buffer)
		self.output.append(filt[-1:])
		self.output.process()

	@property
	def range(self):
		return self.lo, self.hi


class DCBlock(Block):
	input = Input()

	def __init__(self, input, **config):
		self.dc = 0.0
		self.ac = Signal()

		super(DCBlock, self).__init__(**config)

		self.input = input

	def _input_changed(self):
		traits = self.input.trait_get(['label', 'color'])
		self.ac.trait_set(**traits)

	def process(self):
		for x in self.input.new:
			self.dc = self.dc * 0.995 + x * 0.005

		self.ac.append([x - self.dc for x in self.input.new])
		self.ac.process()