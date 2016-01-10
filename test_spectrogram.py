import sys
from PyQt4 import Qt, QtCore, QtGui
from gnuradio import analog, gr, blocks

from blocks import Block, Input, Output, InOutBlock, BarSpectrogram, wireup
from blocks import Stream2Vector, FFT, WaterfallLines


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import numpy as np
import time

class Sine(Block):
    output = Output()

    def init(self, sample_rate, frequency, amplitude=1.0):
        self.gr_block = analog.sig_source_f(sample_rate, analog.GR_SIN_WAVE, frequency, amplitude)
        self.output.sample_rate = sample_rate

class ThrottledNoise(Block):
    output = Output()

    def init(self, sample_rate, amplitude=1.0):
        #self.gr_block = analog.fastnoise_source_f(analog.GR_GAUSSIAN, amplitude)
        self.output.sample_rate = sample_rate        

    def general_work(self, input_items, output_items):
        framerate = 30
        chunk = self.output.sample_rate / framerate
        output_items[0][:chunk] = np.random.random(chunk)
        self.gr_block.produce(0, chunk)

        time.sleep(1.0 / framerate)

        return 0

class Adder(Block):
    a = Input()
    b = Input()

    output = Output(a)

    def init(self):
        self.gr_block = blocks.add_vff()

class Throttle(InOutBlock):
    def init(self):
        #self.gr_block = blocks.throttle(gr.sizeof_float*1, self.input.sample_rate)
        self.gr_block = blocks.throttle(4, 2500.0)


qapp = Qt.QApplication(sys.argv)

top_block = gr.top_block("Spectrogram Test")
sine = Sine(250, 50, 12.3)
noise = ThrottledNoise(250)

signal = Adder(noise, sine)

#spectrogram = BarSpectrogram(signal, bins=256, lo=40, hi=60)

#fft = FFT(Stream2Vector(signal))
#spectrogram = WaterfallLines(fft.bins)
spectrogram = WaterfallLines(signal)


visited = wireup(top_block, spectrogram)

#spec = BarSpectrogram(ch1, lo=0, hi=127, bins=256)

#vec = Stream2Vector(ch1)
#fft = FFT(vec)
#waterfall = WaterfallLines(fft.bins)
#fft = FFT(Stream2Vector(ch1))

spectrogram.widget.show()

            

if __name__ == '__main__':
    top_block.start()

    def quitting():
        top_block.stop()
        #tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None  # to clean up Qt widgets
