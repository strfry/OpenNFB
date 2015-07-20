from flow import Block, Signal

class BandPass(Block):
	def __init__(self, lo, hi, **config):
		super(BandPass, self).__init__(**config)

		self.define_input('input')

		self.output = Signal()

		self.range = (lo, hi)
