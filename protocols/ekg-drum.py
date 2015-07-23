from pyqtgraph.Qt import QtGui, QtCore
from flow import Block, Signal, Input, BandPass
from flow import Spectrograph, Oscilloscope, TextBox

import numpy as np


class HeartAnalyzer(Block):
    input = Input()

    def init(self):
        self.beat = Signal('Beat Event')
        self.bpm = Signal("Beats per Minute")


    def process(self):       
        square = np.array(self.input.buffer) ** 2

        threshold = np.percentile(square, 98)

        if np.max(self.input.buffer[:self.input.new_samples]) > threshold:
            self.beat.append([1.0])
            print 'beat event'
        else:
            self.beat.append([0.0])

        self.beat.process()

        #TODO: implement holdoff time


class MIDIDrum(Block):
    pitch = Input(default=440)
    velocity = Input(default=1.0)
    trigger = Input()

    def init(self, channel=0, port_name='drum'):
        from rtmidi2 import MidiOut
        self.channel = channel
        self.midi = MidiOut().open_virtual_port(port_name)

    def process(self):
        if self.trigger.posedge:
            pitch = self.pitch.value
            vel = self.velocity.value
            self.midi.send_note(channel, pitch, vel)

class EKGDrumFlow(object):
    
    def init(self, context):
        RawEKG = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        print 'RawEKG', RawEKG
        RAWOSC1 = Oscilloscope('Raw Signal', channels=[RawEKG])
        RAWOSC1.autoscale = True


        gridFilter = BandPass(1, 25, input=RawEKG)
        EKG = gridFilter.output
        EKG.color = 'green'

        RAWOSC1.channels.append(EKG)
        RAWOSC1.channels.remove(RawEKG)
        #RAWOSC1.channels.append(RawEKG)


        fftFilt = Spectrograph('Spectrogram', mode='waterfall')
        fftFilt.freq_range = gridFilter.range
        fftFilt.label = 'Frequency Spectrum'

        heart = HeartAnalyzer(input=EKG)

        BPM = TextBox('BPM', label='Heartbeats per minute')
        BPM.input = heart.bpm

        drum = MIDIDrum(port=0)
        drum.trigger = heart.beat


        self.RAWOSC1 = RAWOSC1
        self.fftFilt = fftFilt


    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.RAWOSC1.widget(), 0, 0)
        layout.addWidget(self.fftFilt.widget(), 2, 0)

        return w


def flow():
    return EKGDrumFlow()
