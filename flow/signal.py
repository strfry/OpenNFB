
class Signal(object):
	def __init__(self, label=None):
		latency = 0
		self.label = label
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

	def append_data(self, data):
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