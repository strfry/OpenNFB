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

	def __init__(self, lo, hi, **config):
		super(BandPass, self).__init__(lo=lo, hi=hi, **config)

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


class NotchFilter(Block):
	input = Input()

	frequency = Float(50.0)
	notchWidth = Float(0.1)

	nyquist = Float(125.0)

	@on_trait_change("frequency,notchWidth")
	def compute_filter(self):
		freqRatio = self.frequency / self.nyquist
		print self.frequency, self.nyquist, freqRatio
		print type(self.frequency), type(self.nyquist), type(freqRatio)

		wn = freqRatio
		r = 0.1
		B, A = np.zeros(3), np.zeros(3)
		A[0],A[1],A[2] = 1.0, -2.0*r*np.cos(2*np.pi*wn), r*r
		B[0],B[1],B[2] = 1.0, -2.0*np.cos(2*np.pi*wn), 1.0


		self._filter_b = B
		self._filter_a = A

		#%Compute zeros
		#zeros = np.array([np.exp(0+1j *np.pi*freqRatio ), np.exp( 0-1j*np.pi*freqRatio )])

		#%Compute poles
		#poles = (1-self.notchWidth) * zeros

		#self._filter_b = np.poly( zeros ) # Get moving average filter coefficients
		#self._filter_a = np.poly( poles ) # Get autoregressive filter coefficients

		self._filter_b, self._filter_a = iirfilter(4, (45. / self.nyquist, 55. / self.nyquist), 'bandstop')


	def init(self, input):
		self.input = input

		self.output = Signal()

		self.compute_filter()


	def process(self):
		buffer = self.input.buffer
		filt = lfilter(self._filter_b, self._filter_a, buffer)
		self.output.append(filt[-1:])
		self.output.process()

		#fft = np.fft.fft(self.input.buffer[-256:] * np.hanning(256))
		#fft[90:110] = 0
		#fft[120:140] = 0
		#fft[100:200] = 0
		#ifft = np.fft.ifft(fft)

		#self.output.append([self.input.buffer[-1]])
		#self.output.append(np.real(ifft[-1:]))
		#self.output.process()


	@property
	def range(self):
		return self.lo, self.hi


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
        self.factor = 0.9
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
		self.func = func
		self.args = list(args)

		# Workaround for list event bug 
		self.input = args[0]

		self.output = Signal()

	def process(self):
		args = [chan.last for chan in self.args]
		self.output.append([self.func(*args)])
		self.output.process()

