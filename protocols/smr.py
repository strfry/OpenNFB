from pyqtgraph.Qt import QtGui, QtCore
from flow import Block, Signal, Input, BandPass, DCBlock, RMS, Trendline
from flow import Spectrograph, Oscilloscope, TextBox, BarSpectrogram

import numpy as np

import pyo

from traits.api import Int

class BinauralBeat(Block):
    volume = Input()

    def __init__(self, **config):
        super(BinauralBeat, self).__init__(**config)

        self.server = pyo.Server(buffersize=1024).boot()
        centerFreq = pyo.Sig(256)
        binauralFreq = pyo.Sine(freq=0.05, add=9.5, mul=1.5)

        #left = pyo.Sine(freq=centerFreq - binauralFreq / 2)
        right = pyo.Sine(freq=centerFreq + binauralFreq / 2)
        #left.out(chnl=0)
        #right.out(chnl=1)

        left = pyo.PinkNoise().mix(2).out()

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
        Cz = BandPass(0.0, 25.0, input=Cz)

        self.OSC1 = Oscilloscope('Raw Signal', channels=[BandPass(0.0, 30.0, input=Cz)])
        
        SMR = BandPass(9, 11, input=Cz, order=7)
        self.OSC2 = Oscilloscope('SMR Signal', channels=[SMR])

        SMR_amplitude = RMS(SMR)

        self.OSC3 = Oscilloscope('SMR Amplitude', channels=[SMR_amplitude])

        SMR_trend = Trendline(SMR_amplitude)
        self.OSC4 = Oscilloscope('SMR Trendline', channels=[SMR_trend])

        self.bb = BinauralBeat(volume=SMR_amplitude)

        self.Spec = BarSpectrogram('Cz Spectrogram', input=BandPass(0.1, 30.0, input=Cz, order=6))

    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.OSC1.widget(), 0, 0)
        layout.addWidget(self.OSC2.widget(), 1, 0)
        layout.addWidget(self.OSC3.widget(), 2, 0)
        layout.addWidget(self.OSC4.widget(), 3, 0)

        layout.addWidget(self.Spec.widget(), 0, 1, 4, 1)

        return w



def flow():
    return SMRFlow()
