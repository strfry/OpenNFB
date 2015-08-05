from pyqtgraph.Qt import QtGui
from flow import *

class EMGFlow(object):
    
    def init(self, context):
        ch1 = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        ch1 = DCBlock(ch1).ac
        #Cz = BandPass(0.0, 35.0, input=Cz)

        self.OSC1 = Oscilloscope('Raw Signal', channels=[ch1])
        
        amplitude = RMS(ch1)

        self.OSC2 = Oscilloscope('Amplitude', channels=[amplitude])

        trend = Trendline(amplitude)
        self.OSC3 = Oscilloscope('EMG Trendline', channels=[trend])

        self.Spec = BarSpectrogram('Spectrogram', input=ch1)

    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.OSC1.widget(), 0, 0)
        layout.addWidget(self.OSC2.widget(), 1, 0)
        layout.addWidget(self.OSC3.widget(), 2, 0)

        layout.addWidget(self.Spec.widget(), 0, 1, 3, 1)

        return w



def flow():
    return EMGFlow()
