from pyqtgraph.Qt import QtGui, QtCore
from flow import Block, Signal, Input, BandPass, DCBlock, RMS, Trendline
from flow import Spectrograph, Oscilloscope, TextBox, BarSpectrogram

import numpy as np



class MultibandFlow(object):
    
    def init(self, context):
        channel1 = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        dcblock = DCBlock(channel1)
        channel1 = BandPass(0.0, 30.0, input=dcblock.ac, order=6)

        self.OSC1 = Oscilloscope('Raw Signal', channels=[channel1])

        alpha = BandPass(9, 11, input=channel1)
        theta = BandPass(5, 7, input=channel1)
        delta = BandPass(1.5, 3, input=channel1)
        lobeta = BandPass(13, 15, input=channel1)
        hibeta = BandPass(15, 20, input=channel1)

        alpha.output.color = 'green'
        theta.output.color = 'orange'
        delta.output.color = 'red'
        lobeta.output.color = 'blue'
        hibeta.output.color = 'cyan'

        chanlist = [alpha, 
            theta,
            delta,
            lobeta, hibeta]

        self.OSC2 = Oscilloscope('Band Signal', channels=chanlist)

        amplitudes = [RMS(channel) for channel in chanlist]

        self.OSC3 = Oscilloscope('Amplitude', channels=amplitudes)

        trends = [Trendline(channel) for channel in amplitudes]
        self.OSC4 = Oscilloscope('SMR Trendline', channels=trends)

        self.Spec = BarSpectrogram('Spectrogram', input=channel1)

        dctrend = Trendline(dcblock.dc)
        self.DCOSC = Oscilloscope('DC Trend', channels=[dctrend])

    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.OSC1.widget(), 0, 0)
        layout.addWidget(self.OSC2.widget(), 1, 0)
        layout.addWidget(self.OSC3.widget(), 2, 0)
        layout.addWidget(self.OSC4.widget(), 3, 0)

        layout.addWidget(self.Spec.widget(), 0, 1, 3, 1)
        layout.addWidget(self.DCOSC.widget(), 3, 1)

        return w



def flow():
    return MultibandFlow()
