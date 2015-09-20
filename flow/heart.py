from flow import Block, Signal, Input
from flow import RMS

import numpy as np

class PulseAnalyzer(Block):
	input = Input()

	def init(self, input):
		self.input = input

		self.output = Signal()
		self.bpm = Signal()
		self.gradient = Signal()
		self.pulse = Signal()

		self.last_beat = -1
		self.timestamp = 0

	def _input_changed(self):
		self.output.copy_traits(self.input, ['label', 'color'])

	def process(self):
		avg = np.average(self.output.buffer)
		max = np.max(self.output.buffer)

		self.timestamp += 1

		self.gradient.append([self.input.buffer[-1] - self.input.buffer[-2]])

		buf = np.power(self.gradient.buffer[-50:], 2)
		s = np.sum(np.hanning(50)[:50] * buf)
		
		self.output.append([s])

		for i, sample in enumerate(self.output.new):
			new = 0.1 if sample > max * 0.5 else 0.0
			self.pulse.append([new])

			if new > self.pulse.buffer[-2]:
				diff = self.timestamp - self.last_beat
				bpm = 1.0 / (diff / 250.) * 60

				self.bpm.append([bpm])
				self.bpm.process()

				print ('beat event', diff, bpm, self.timestamp, self.last_beat)


				self.last_beat = self.timestamp

		self.output.process()
		self.gradient.process()
