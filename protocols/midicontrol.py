from pyqtgraph.Qt import QtGui, QtCore
from flow import Block, Signal, Input, BandPass, DCBlock
from flow import Spectrograph, Oscilloscope, TextBox

import numpy as np


import pyqtgraph as pg

class SpectrumBars(Block):
    input = Input()

    def init(self):
        self.bands = [4, 8, 12, 15, 20, 30, 50]
        self.band_names = ['Theta', 'Alpha', 'SMR', 'Beta', 'Hi Beta', 'Gamma']

        num_bands = len(self.band_names)
        assert len(self.bands) == num_bands + 1

        self.plot = pg.PlotWidget()
        self.bars = pg.BarGraphItem(x=range(num_bands), height=range(num_bands), width=0.5)
        self.plot.addItem(self.bars)

        self.plot.getAxis('bottom').setTicks([enumerate(self.band_names)])

        self.bars.setOpts(brushes=[pg.hsvColor(float(x) / num_bands) for x in range(num_bands)])

        self.cnt = 0

    def process(self):
        C = np.fft.fft(self.input.buffer)

        self.cnt += 1
        if self.cnt == 20:
            self.cnt = 0
        else:
            return

        C = abs(C)
        Fs = 250

        Power = np.zeros(len(self.bands)-1);
        for Freq_Index in xrange(0,len(self.bands)-1):
            Freq = float(self.bands[Freq_Index])
            Next_Freq = float(self.bands[Freq_Index+1])
            Power[Freq_Index] = sum(C[np.floor(Freq/Fs*len(C)):np.floor(Next_Freq/Fs*len(C))])
        Power_Ratio = Power/sum(Power)

        self.bars.setOpts(height=Power_Ratio)

    def widget(self):
        return self.plot

from traits.api import Float

class Normalizer(Block):
    input = Input()
    time_factor = Float(0.5)

    def __init__(self, input, **config):
        self.output = Signal()

        super(Normalizer, self).__init__(**config)

        self.min = 0.0
        self.max = 1.0

        self.input = input

    def process(self):

        min = np.min(self.input.buffer)
        self.min = self.min * self.time_factor + min * (1.0 - self.time_factor)

        max = np.max(self.input.buffer)
        self.max = self.max * self.time_factor + max * (1.0 - self.time_factor)

        out = (np.array(self.input.new) - min) / (max - min)
        self.output.append(out)
        self.output.process()


class MidiControl(Block):
    cc1 = Input()
    cc2 = Input()

    def init(self, channel=0, port_name='nfb'):
        from rtmidi2 import MidiOut
        self.channel = channel
        self.midi = MidiOut().open_virtual_port(port_name)

    def process(self):
        clamp = lambda x, mi, ma: max(min(ma, x), mi)
        val = clamp(self.cc1.buffer[-1] * 127, 0, 127)

        self.midi.send_cc(0, 1, val)
        #self.midi.send_pitchbend(0, random.random() * 8000)

from traits.api import Int

class Intensity(Block):
    input = Input()
    avg_size = Int(15)

    def __init__(self, input, **config):
        self.output = Signal()

        super(Intensity, self).__init__(**config)

        self.input = input


    def process(self):
        rms = sum(np.array(self.input.buffer) ** 2) / len(self.input.buffer)
        avg = np.sqrt(rms)

        self.output.append([avg])
        self.output.process()


class MusicControl(object):
    
    def init(self, context):
        Fz = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        Fz = DCBlock(Fz).ac
        Fz = BandPass(1.0, 25.0, input=Fz).output

        Osci1 = Oscilloscope('Raw Signal', channels=[Fz])

        Alpha = Intensity(BandPass(8.0, 12.0, input=Fz).output).output
        Alpha = Normalizer(Alpha).output

        MidiControl(cc1=Alpha)

        Osci2 = Oscilloscope('Intensity', channels=[Alpha])
        Osci2.autoscale = False

        fftFilt = Spectrograph('Spectrogram', mode='waterfall')
        #fftFilt.freq_range = gridFilter.range
        #fftFilt.label = 'Frequency Spectrum'

        self.RAWOSC1 = Osci1
        self.OSC2 = Osci2
        self.fftFilt = fftFilt
        self.bars = SpectrumBars(input=Fz)


    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.RAWOSC1.widget(), 0, 0)
        layout.addWidget(self.OSC2.widget(), 1, 0)
        layout.addWidget(self.bars.widget(), 2, 0)

        return w


def flow():
    return MusicControl()
