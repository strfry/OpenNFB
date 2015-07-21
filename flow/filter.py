from flow import Block, Signal, Input

class BandPass(Block):
	input = Input()

	def __init__(self, lo, hi, **config):
		super(BandPass, self).__init__(**config)

		self.output = Signal()

		self.range = (lo, hi)

	def process(self):
		self.output.append_data([0])
		self.output.process()
