import numpy as np
from traits.api import HasTraits, Color, Str

class Signal(HasTraits):
	color = Color()
	label = Str()

	def __init__(self, label='', **config):
		super(Signal, self).__init__(**config)

		self.label = label

		latency = 0
		self.connections_ = set()

		self.buffer = [0] * 256
		self.new_samples = 0

		self.timestamp = 0


	# Store a connection to connected input blocks
	def _connect(self, block):
		self.connections_.add(block)
		print '_connect', self, block

	def _disconnect(self, block):
		self.connections_.remove(block)

	def clear_connections(self):
		self.connections_.clear()

	def append(self, data):
		size = len(self.buffer)

		self.buffer[:-len(data)] = self.buffer[len(data):]
		self.buffer[-len(data):] = data

		self.new_samples = len(data)

		self.timestamp += len(data)

	def process(self):
		for c in self.connections_:
			c._signal_ready(self)

	@property
	def new(self):
		return self.buffer[-self.new_samples:]

	@property
	def posedge(self):
		new = self.buffer[: self.new_samples + 1]
		new = np.array(new) >= 1.0

		argmax = np.argmax(new[:-1])
		if new[argmax] and not new[argmax + 1]:
			return True
		return False
