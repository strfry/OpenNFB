from pyqtgraph.Qt import QtGui, QtCore
from flow import *

import numpy as np

import pyo

from traits.api import Int

class BinauralBeat(Block):
    volume = Input()

    def __init__(self, **config):
        super(BinauralBeat, self).__init__(**config)

        self.server = pyo.Server(buffersize=1024).boot()
        centerFreq = pyo.Sig(256)
        binauralFreq = pyo.Sine(freq=0.05, add=10.5, mul=1.5)

        left = pyo.Sine(freq=centerFreq - binauralFreq / 2)
        right = pyo.Sine(freq=centerFreq + binauralFreq / 2)
        left.out(chnl=0)
        right.out(chnl=1)

        #left = pyo.PinkNoise().mix(2).out()

        import thread
        thread.start_new_thread(self.server.start, ())

        self.left = left
        self.right = right

    def process(self):
        vol = float(self.volume.buffer[-1] / 3500.0)
        vol = min(vol, 1.0)
        self.left.mul = self.right.mul = vol




class SMRFlow(object):
    
    def init(self, context):
        C3C4 = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        ch1 = DCBlock(C3C4).ac
        ch1 = BandPass(0.0, 35.0, input=ch1)
        ch1 = DCBlock(ch1).ac

        self.OSC1 = Oscilloscope('Raw Signal', channels=[BandPass(0.0, 30.0, input=ch1)])
        
        SMR = BandPass(11.5, 14.5, input=ch1, color='yellow')
        Theta = BandPass(2, 6, input=ch1, order=6, color='orange')
        hibeta = BandPass(23, 32, input=ch1, order=6, color='cyan')
        
        SMR = Expression(lambda x: x*25, SMR)
        
        SMR.output.color = 'yellow'
        Theta.output.color='orange'
        hibeta.output.color='cyan'
        
        SMR_rms = RMS(SMR)
        Theta_rms = RMS(Theta)
        hibeta_rms = RMS(hibeta)
        
        rms_channels = [SMR_rms, Theta_rms, hibeta_rms]
        
        self.OSC2 = Oscilloscope('intensities', channels=rms_channels)

        self.OSC3 = Oscilloscope('SMR Trendline', channels=[Trendline(x) for x in rms_channels])

        score = Expression(lambda L, T, H: L - T /4 - H/2, SMR_rms, Theta_rms, hibeta_rms)
        self.Lthr = Threshold('SMR', input=SMR_rms, mode='increase', auto_target=90)
        self.Tthr = Threshold('Theta', input=Theta_rms, mode='decrease', auto_target=93)
        self.Hthr = Threshold('Hi Beta', input=hibeta_rms, mode='decrease', auto_target=92)
        enable = enable=Expression(lambda *x: all(x), self.Lthr.passfail, self.Tthr.passfail, self.Hthr.passfail)

        self.Spec = BarSpectrogram('Spectrogram', input=BandPass(0.1, 30.0, input=ch1))
        
        import os
        if 'MOVIE' in os.environ:
             self.mplayer = MPlayerControl(os.environ['MOVIE'], enable=enable)
        else:
             self.bb = BinauralBeat(volume=score)

    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.OSC1.widget(), 0, 0)
        layout.addWidget(self.OSC2.widget(), 1, 0)
        layout.addWidget(self.OSC3.widget(), 2, 0)

        layout.addWidget(self.Spec.widget(), 0, 1, 3, 3)
        layout.addWidget(self.Lthr.widget(), 4, 1, 1, 1)
        layout.addWidget(self.Tthr.widget(), 4, 2, 1, 1)
        layout.addWidget(self.Hthr.widget(), 4, 3, 1, 1)

        return w



def flow():
    return SMRFlow()
