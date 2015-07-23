import numpy as np
from traits.api import HasTraits, Color, Str

class Signal(HasTraits):
	color = Color()
	label = Str()

	def __init__(self, label='', **config):
		super(Signal, self).__init__(**config)

		self.label = label

		latency = 0
		self.connections = set()

		self.buffer = [0] * 256
		self.new_samples = 0

		self.timestamp = 0


	# Store a connection to connected input blocks
	def _connect(self, block):
		self.connections.add(block)
		print '_connect', self, block

	def _disconnect(self, block):
		self.connections.remove(block)

	def append(self, data):
		size = len(self.buffer)
		data = list(data)
		data.reverse()

		self.buffer[len(data):] = self.buffer[:-len(data)]
		self.buffer[:len(data)] = data

		self.new_samples = len(data)

		self.timestamp += len(data)

	def process(self):
		for c in self.connections:
			c._signal_ready(self)


	@property
	def posedge(self):
		new = self.buffer[: self.new_samples + 1]
		new = np.array(new) >= 1.0

		argmax = np.argmax(new[:-1])
		if new[argmax] and not new[argmax + 1]:
			return True
		return False
