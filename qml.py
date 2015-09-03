
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *
from PyQt5.QtQuickWidgets import *
from PyQt5.QtQml import *

import sys
import signal as _signal

from acquisition import UDPThread
from flow import *

_signal.signal(_signal.SIGINT, _signal.SIG_DFL)
myApp = QApplication(sys.argv)
qmlEngine = QQmlEngine()

VideoPlayer = QQmlComponent(qmlEngine, QUrl('file:NeuroWidgets/video.qml'))


quickWindow = QQuickWindow()

videoPlayer = VideoPlayer.create()
videoPlayer.setParentItem(quickWindow.contentItem())

counter = 0

def setup_flow(context):
	global OSC1

	ch1_raw = context.get_channel('Channel 1')	

	ch1 = DCBlock(ch1_raw).ac

	ch1 = BandPass(1.0, 25.0, input=ch1)
	ch1 = BandPass(1.0, 25.0, input=ch1)
	ch1 = BandPass(1.0, 25.0, input=ch1)
	#ch1 = BandPass(1.0, 25.0, input=ch1)



	OSC1 = Oscilloscope('Raw', channels=[ch1])
	Spec = BarSpectrogram('Raw Spec', input=ch1)

	smr = BandPass(11.5, 14.5, input=ch1)
	smr = Averager(RMS(smr))

	beta = BandPass(18, 25, input=ch1)
	beta = Averager(RMS(beta))

	#total_rms = Averager(RMS(ch1))

	#smr = Expression(lambda x, y: x / y, smr, total_rms)
	smr.output.color = 'green'
	beta.output.color = 'blue'


	OSC2 = Oscilloscope('Intensity', channels=[smr, beta])

	layout = QGridLayout()
	layout.addWidget(OSC1.widget())
	layout.addWidget(Spec.widget())
	layout.addWidget(OSC2.widget())

	

	def update_qml(smr, beta):
		bias = 0.3
		factor = 1

		# Very important to cast to float here, Qt silently ignores numpy types
		
		# Beta 10-40, Target 1-10
		brightness = float(1.0 - beta / 10)
		brightness = float(smr / beta) / 0.035 - 1.0

		volume = float(smr / beta) / 0.045 - 1.0


		videoPlayer.setProperty('brightness', brightness)
		videoPlayer.setProperty('volume', volume)

		global counter
		#if not counter: counter = 0
		counter += 1
		if counter > 50:
			counter = 0
			videoPlayer.setProperty('speed', brightness)
			print ('beta ', beta, 'smr ', smr, 'smr/beta ', volume)

		return 0.0

	foo = Expression(update_qml, smr, beta)



	return layout

context = Context()
context.register_channel('Channel 1')
context.register_channel('Channel 2')
layout = setup_flow(context)

analysisWindow = QWidget()
analysisWindow.setLayout(layout)
analysisWindow.show()

sourceThread = UDPThread()

quickWindow.show()
#quickWindow.showFullScreen()

def handlePacket(packet):
	context.append_channel_data('Channel 1', [packet[0]])
	context.append_channel_data('Channel 2', [packet[1]])
	context.process()

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()

def updateGUI():
	for child in analysisWindow.children():
		if hasattr(child, 'block'):
			child.block.updateGUI()
	#		pass

guiTimer = QtCore.QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)

myApp.exec_()
sys.exit()
