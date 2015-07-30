from pyqtgraph.Qt import QtGui, QtCore
from flow import Block, Signal, Input, BandPass, DCBlock
from flow import Spectrograph, Oscilloscope, TextBox

import numpy as np

import pyo

class Amplitude(Block):
    input = Input()

    def __init__(self, input):
        self.output = Signal()
        super(Amplitude, self).__init__(input=input)

    def process(self):
        ampl = sum(np.abs(self.input.new))

        self.output.append([ampl])
        self.output.process()

class Averager(Block):
    input = Input()

    def __init__(self, input):
        self.output = Signal()
        self.average = 0.0
        self.factor = 0.99
        super(Averager, self).__init__(input=input)

    def process(self):
        for x in self.input.new:
            self.average = self.average * self.factor + x * (1.0 - self.factor)
            self.output.append([self.average])

        self.output.process()


from traits.api import Int

class Trendline(Block):
    input = Input()
    interval = Int(25)

    def __init__(self, input):
        self.output = Signal(buffer_size=4000)
        self.cnt = 0

        super(Trendline, self).__init__(input=input)

    def process(self):
        self.cnt += self.input.new_samples
        if self.cnt >= self.interval:
            self.cnt = 0

            avg = sum(self.input.buffer[-self.interval:]) / self.interval

            self.output.append([avg])
            self.output.process()

class BinauralBeat(Block):
    volume = Input()

    def __init__(self, **config):
        super(BinauralBeat, self).__init__(**config)

        self.server = pyo.Server(buffersize=1024).boot()
        centerFreq = pyo.Sig(256)
        binauralFreq = pyo.Sine(freq=0.05, add=13.5, mul=1.5)

        left = pyo.Sine(freq=centerFreq - binauralFreq / 2)
        right = pyo.Sine(freq=centerFreq + binauralFreq / 2)
        left.out(chnl=0)
        right.out(chnl=1)

        left.mul = right.mul = 0.2


        import thread
        thread.start_new_thread(self.server.start, ())

        self.left = left
        self.right = right

    def process(self):
        vol = float(self.volume.buffer[-1] / 1500.0)
        vol = min(vol, 1.0)
        self.left.mul = self.right.mul = vol




class SMRFlow(object):
    
    def init(self, context):
        Cz = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        Cz = DCBlock(Cz).ac

        self.OSC1 = Oscilloscope('Raw Signal', channels=[BandPass(0.0, 30.0, input=Cz).output])
        
        SMR = BandPass(12, 15, input=Cz, order=6).output
        self.OSC2 = Oscilloscope('SMR Signal', channels=[SMR])

        SMR_amplitude = Averager(Amplitude(SMR).output).output

        self.OSC3 = Oscilloscope('SMR Amplitude', channels=[SMR_amplitude])

        SMR_trend = Trendline(SMR_amplitude).output

        self.OSC4 = Oscilloscope('SMR Trendline', channels=[SMR_trend])

        self.bb = BinauralBeat(volume=SMR_amplitude)


        

    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.OSC1.widget(), 0, 0)
        layout.addWidget(self.OSC2.widget(), 1, 0)
        layout.addWidget(self.OSC3.widget(), 2, 0)
        layout.addWidget(self.OSC4.widget(), 3, 0)

        return w



def flow():
    return SMRFlow()
