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

	@on_trait_change("lo,hi,order")
	def _range_changed(self):
		print 'range changed: ', self.lo, self.hi, self.order
		b,a = iirfilter(self.order, (self.lo / self.nyquist, self.hi / self.nyquist))

		self._filter_b, self._filter_a = b,a

	def process(self):
		buffer = list(self.input.buffer)
		buffer.reverse()
		filt = lfilter(self._filter_b, self._filter_a, buffer)
		self.output.append(filt[-1:])
		self.output.process()

	@property
	def range(self):
		return self.lo, self.hi
