

class BandPass(InOutBlock):    
    def init(self, lo, hi): 
        nyquist = self.input.sample_rate / 2.0
        Wp = [lo / nyquist, hi / nyquist]
        #Ws = [(lo - 1) / nyquist, (hi+1) / nyquist]
        #b, a = scipy.signal.iirdesign(Wp, Ws, 0.1, 60.0)
        b, a = scipy.signal.iirfilter(6, Wp, btype='bandpass',
            ftype='ellip', rp=0.1, rs=60.0)

        #self.gr_block = filter.iir_filter_ffd(a, b, oldstyle=False)
        self.gr_block = filter.iir_filter_ffd(b, a, oldstyle=False)

class NotchFilter(InOutBlock):
    def init(self, freq=50.0, mod=0.9):
        theta = 2 * np.pi * 50 / self.input.sample_rate
        zero = np.exp(np.array([1j, -1j]) * theta)
        pole = mod * zero

        a, b = np.poly(pole), np.poly(zero)
        #notch_ab = numpy.poly(zero), numpy.poly(pole)
        #notch_ab = scipy.signal.iirfilter(32, [30.0 / 125], btype='low')

        self.gr_block = filter.iir_filter_ffd(b, a, oldstyle=False)
        

class RMS(InOutBlock):
    def init(self, alpha=0.01):
        self.gr_block = blocks.rms_ff(alpha)


class DCBlock(InOutBlock):
    def init(self, taps=16):
        self.gr_block = filter.dc_blocker_ff(16, long_form=False)

class ExponentialAverage(InOutBlock):
    def init(self, lookback = 1.0):
        samples = length * self.input.sample_rate
        scale = 1.0 / samples
        self.gr_block = blocks.moving_average_ff(int(samples), scale)



    def general_work(self, input_items, output_items):
        print ('BarSpectrogram work', len(input_items[0]), output_items, input_items[0][0])

        self.gr_block.consume_each(1)
        self.gr_block.produce_each(1)

        output_items[0][0] = result

        self.buffer = input_items[0][-len(self.win):]
        return 0




class Stream2Vector(Block):
    input = Input()
    output = Output(type=(np.float32, 256))

    def init(self, bins=256, framerate=2):
        self.num_samples = int(self.input.sample_rate / framerate)

        self.gr_block.set_history(bins)
        self.bins = bins

    def general_work(self, input_items, output_items):
        self.gr_block.consume_each(self.num_samples)

        print 'Stream2Vector work', len(input_items[0])

        #output_items[0][:self.bins] = input_items[0][-self.bins:]
        output_items[0][0] = input_items[0][-self.bins:]
        #self.gr_block.produce(0, self.bins)
        self.gr_block.produce(0, 1)

        return 0

class FFT(Block):
    input = Input()
    bins = Output()

    def init(self, bins=256):
        self.gr_block = fft.fft_vfc(256, forward=True, window=fft.window.blackmanharris(bins))

