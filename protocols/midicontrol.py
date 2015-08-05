from pyqtgraph.Qt import QtGui, QtCore
from flow import Block, Signal, Input, BandPass, DCBlock, BarSpectrogram
from flow import Spectrograph, Oscilloscope, TextBox, RMS

import numpy as np
import pyqtgraph as pg

from traits.api import Float

class Normalizer(Block):
    input = Input()
    time_factor = Float(0.9999)

    def __init__(self, input, **config):
        self.output = Signal()

        super(Normalizer, self).__init__(**config)

        self.min = 0.0
        self.max = 1.0

        self.input = input

    def process(self):

        min = np.min(self.input.buffer) / 2
        self.min = self.min * self.time_factor + min * (1.0 - self.time_factor)

        max = np.max(self.input.buffer) * 2
        self.max = self.max * self.time_factor + max * (1.0 - self.time_factor)

        out = (np.array(self.input.new) - self.min) / (self.max - self.min) * 2
        self.output.append(out)
        self.output.process()


from traits.api import Dict, Range, on_trait_change
import random

class MidiControl(Block):
    cc = Dict(Range(0, 127), Input)

    def init(self, channel=0, port_name='nfb'):
        from rtmidi2 import MidiOut
        self.channel = channel
        self.midi = MidiOut().open_virtual_port(port_name)

        self.config_button = QtGui.QToolButton()
        self.config_button.clicked.connect(self.config_dialog)
        self.config_button.block = self

        self.config = False

        #self.on_trait_change()
        #self.config_dialog()

    def config_dialog(self):
        self.config = True
        win = QtGui.QDialog()

        layout = QtGui.QVBoxLayout()

        keys = self.cc.keys()
        keys.sort()

        for cc in keys:
            label = "CC " + str(cc)
            button = QtGui.QPushButton(label)
            func = lambda cc=cc: self.midi.send_cc(0, cc, random.randint(0, 127))
            button.pressed.connect(func)
            layout.addWidget(button)

        finishButton = QtGui.QPushButton('Finished')
        layout.addWidget(finishButton)
        finishButton.clicked.connect(win.accept)

        win.setLayout(layout)

        win.exec_()
        self.config = False

    def updateGUI(self):
        if self.config: return

        clamp = lambda x, mi, ma: max(min(ma, x), mi)
        for cc in self.cc:
            sig = self.cc[cc]
            val = clamp(sig.buffer[-1] * 127, 0, 127)

            self.midi.send_cc(0, cc, val)
        #self.midi.send_pitchbend(0, random.random() * 8000)

    def widget(self):
        return self.config_button


class DominantFrequency(Block):
    input = Input()

    chunk_size = 256

    def init(self, input):
        self.input = input
        self.cnt = 0

        self.window = np.hanning(self.chunk_size)

        self.freq = Signal()

    def process(self):
        self.cnt += 1
        if self.cnt > 20:
            self.cnt = 0
        else:
            return


        C = np.fft.rfft(self.input.buffer[-self.chunk_size:] * self.window)
        C = abs(C)
        Fs = 250.0

        def index_max(values):
            return max(xrange(len(values)),key=values.__getitem__)

        freq = index_max(C)
        freq = freq / Fs

        self.freq.append([freq])
        self.freq.process()


class MusicControl(object):
    
    def init(self, context):
        Fz = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        Fz = DCBlock(Fz).ac
        Fz = BandPass(1.0, 25.0, input=Fz)

        Osci1 = Oscilloscope('Raw Signal', channels=[Fz])

        Alpha = RMS(BandPass(9.0, 11.0, input=Fz))
        Alpha = Normalizer(Alpha)

        self.midi = MidiControl(cc={23: Alpha})
        self.midi.cc[1] = Normalizer(RMS(BandPass(4, 8, input=Fz)))
        #self.midi.cc[2] = Normalizer(Intensity(BandPass(15, 18, input=Fz)))
        #self.midi.cc[3] = Normalizer(Intensity(BandPass(18, 21, input=Fz)))

        #dom_freq = DominantFrequency(Fz).freq
        #dom_freq.color = 'green'
        #self.midi.cc[4] = dom_freq

        Osci2 = Oscilloscope('Intensity', channels=[Alpha])
        Osci2.autoscale = False

        self.midi.cc[1].color = 'red'
        Osci2.channels.append(self.midi.cc[1])

        #fftFilt = Spectrograph('Spectrogram', mode='waterfall')
        #fftFilt.freq_range = gridFilter.range
        #fftFilt.label = 'Frequency Spectrum'

        self.RAWOSC1 = Osci1
        self.OSC2 = Osci2
        #self.fftFilt = fftFilt
        self.bars = BarSpectrogram('Spectrogram', input=Fz)


    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.RAWOSC1.widget(), 0, 0)
        layout.addWidget(self.OSC2.widget(), 1, 0)
        layout.addWidget(self.bars.widget(), 2, 0)

        layout.addWidget(self.midi.widget(), 0, 1, 3, 1)

        return w


def flow():
    return MusicControl()
