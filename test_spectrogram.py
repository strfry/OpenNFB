import sys
from PyQt4 import Qt, QtCore, QtGui
from gnuradio import analog, gr, blocks

from blocks import Block, Input, Output, BarSpectrogram, wireup


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class Sine(Block):
    output = Output()

    def init(self, sample_rate, frequency, amplitude=1.0):
        self.gr_block = analog.sig_source_f(sample_rate, analog.GR_SIN_WAVE, frequency, amplitude)
        self.output.sample_rate = sample_rate

class Noise(Block):
    output = Output()

    def init(self, sample_rate, amplitude=1.0):
        self.gr_block = analog.fastnoise_source_f(analog.GR_GAUSSIAN, amplitude)
        self.output.sample_rate = sample_rate        

class Adder(Block):
    a = Input()
    b = Input()

    output = Output(a)

    def init(self):
        self.gr_block = blocks.add_vff()


qapp = Qt.QApplication(sys.argv)

top_block = gr.top_block("Spectrogram Test")
sine = Sine(250, 50, 2.3)
noise = Noise(250)

signal = Adder(noise, sine)

spectrogram = BarSpectrogram(signal)


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
