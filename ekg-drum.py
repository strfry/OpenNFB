from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from scipy.special import expit
from transformations import FFT, GridFilter, IIRFilter
from widgets import ScrollingPlot
from SpectrographWidget import SpectrographWidget

RawEKG = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

RAWOSCI = Oscilloscope('Raw Signal', channels=[RawEKG])
RAWOSC1.autoscale(True)

gridFilter = BandPass(1, 25, input=RawEKG)
EKG = gridFilter.output
EKG.color = 'green'

RAWOSC1.channel[1] = EKG

fftFilt = Spectrograph('Spectrogram', mode='waterfall')
fftFilt.freq_range = gridFilter.range
fftFilt.label = 'Frequency Spectrum'


#filteredPlot = ScrollingPlot()
#filteredPlot.plot('ac', pen='r')
#filteredPlot.plot('abs', pen='g')

class HeartAnalyser(Block):
    def init(self):
        self.create_input('input')





    def process(self):




heart = HeartAnalyzer(input=Fz1)

class MIDIDrum(Block):
    def init(self, port):
        import rtmidi2.MidiOut as MidiOut
        self.midi = MidiOut(0)

        self.create_input('pitch', default=440)
        self.create_input('velocity', default=1.0)
        self.create_input('trigger')

    def process(self):
        if self.trigger.posedge:
            pitch = self.pitch.value
            vel = self.velocity.value
            self.midi.send_note(0, pitch, vel)


BPM = TextBox('BPM', label='Heartbeats per minute')
BPM.input = heart.bpm

drum = MIDIDrum(0)
drum.trigger = heart.beat

def widget():
    w = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    w.setLayout(layout)

    layout.addWidget(RAWOSC1, 0, 0)
    layout.addWidget(, 1, 0)
    layout.addWidget(heartbeatPlot, 3, 0)

    return w

class Heartbeat(object):
    def __init__(self, window=500):
        self.out = 0
        self.buffer = np.zeros(window)
        self.threshold = 0.0
        self.lastBeat = 0

        self.sound = QtGui.QSound('drum.wav')

        self.midi_out = rtmidi2.MidiOut()
        # open the first available port
        self.midi_out.open_port(0)
        # send C3 with vel. 100 on channel 1
        pass

    def process(self, newValue):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = newValue

        self.threshold = np.percentile(self.buffer, 98)

        beat = 10000.0 if newValue > self.threshold else 0.0

        self.lastBeat += 1

        if beat > 0 and self.lastBeat > 50:
            self.lastBeat = 0
            self.beat = 10000.0
            #self.sound.play()
            print "beat event"
            self.midi_out.send_noteon(0, 48, 100)
        else:
            self.beat = 0.0



hb = Heartbeat()

def update(channels):
    rawPlot.update('raw', channels[0])

    gridFilter.update(channels[0])

    filteredPlot.update('ac', gridFilter.ac)
    filteredPlot.update('abs', abs(gridFilter.ac))

    hb.process(abs(gridFilter.ac))
    heartbeatPlot.update('ekg', hb.buffer[-1])
    heartbeatPlot.update('percentile', hb.threshold)


    heartbeatPlot.update('beat', hb.beat)

