import scipy.signal
import numpy as np
ptr = 0

class FFT(object):
    def __init__(self, bins=256, samplingFrequency = 250):
        self.bins = bins
        self.buffer = np.zeros(bins)
        self.Fs = samplingFrequency
        self.window = np.hanning(bins)


    def update(self, newValue):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = newValue

        self.fft = np.fft.fft(self.buffer * self.window)

    def bandPower(self, low, high):
        low = float(low)
        high = float(high)
        C = abs(self.fft)
        power = sum(C[np.floor(low/self.Fs*len(C)):np.floor(high/self.Fs*len(C))])
        return power

class IIRFilter(object):
    def __init__(self, order = 13, samplingFrequency=250, gridFrequency=50.0):
        self.buffer = np.zeros(300) 
        self.b, self.a = scipy.signal.iirfilter(7, (1. / 250, 35. / 250), btype='bandpass')

        #self.fir = scipy.signal.firwin(90, (4.0, 35.0), pass_zero=False, nyq=125.0)
        self.order = order
        self.cache = {}
        self.dc = 0
        self.dc2 = .0

    def update(self, newValue):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = newValue - self.dc
        
        self.dc = 0.99 * self.dc + newValue * 0.01

        filterBuffer = self.buffer[-50:] # Limit the processing length to the order of the filter
        self.ac = scipy.signal.lfilter(self.a, self.b, filterBuffer)[-1]
        #self.ac = scipy.signal.lfilter(self.fir, [1.0], filterBuffer - self.dc)[0

    def band(self, lo, hi):
        if (lo, hi) not in self.cache:
          self.cache[(lo, hi)] = scipy.signal.iirfilter(self.order, (lo / 250., hi / 250.), btype='bandpass')
        b, a = self.cache[(lo, hi)]
        filterBuffer = self.buffer[-100:]
        filt = scipy.signal.lfilter(b, a, filterBuffer)
        
        self.dc2 = self.dc2 * 0.99 + .01 * filt[-1]

        
	result = filt - self.dc2
	
	global ptr
	ptr += 1
	if ptr % 100 == 0:
	  print self.dc, self.buffer[-1], result[-1]



        return result[-1]




class GridFilter(object):
    def __init__(self, samplingFrequency=250, gridFrequency=50.0):
        self.buffer = np.zeros(100)
        self.b, self.a = scipy.signal.iirfilter(7, (48. / 250, 52. / 250), btype='bandstop'
    )

        #self.fir = scipy.signal.firwin(90, (4.0, 35.0), pass_zero=False, nyq=125.0)

    def update(self, newValue):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = newValue

        self.dc = np.mean(self.buffer)


        filterBuffer = self.buffer # Limit the processing length to the order of the filter
        self.ac = scipy.signal.lfilter(self.a, self.b, filterBuffer - self.dc)[-1]
        #self.ac = scipy.signal.lfilter(self.fir, [1.0], filterBuffer - self.dc)[0


