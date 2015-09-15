
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

	ch1 = BandPass(0.01, 32.0, input=ch1)
	ch1 = BandPass(0.01, 32.0, input=ch1)
	#ch1 = BandPass(1.0, 32.0, input=ch1)



	OSC1 = Oscilloscope('Raw', channels=[ch1])
	Spec = BarSpectrogram('Raw Spec', input=ch1)

	reward = BandPass(9, 12, input=ch1)
	reward = Averager(RMS(reward))

	inhibit1 = BandPass(18, 32, input=ch1)
	inhibit1 = Averager(RMS(inhibit1))

	inhibit2 = BandPass(1, 7, input=ch1)
	inhibit2 = Averager(RMS(inhibit2))

	total = DCBlock(RMS(ch1)).dc

	#total_rms = Averager(RMS(ch1))

	#reward = Expression(lambda x, y: x / y, reward, total_rms)
	reward.output.color = 'green'
	inhibit1.output.color = 'cyan'
	inhibit2.output.color = 'violet'

	reward_ = Expression(lambda x, total: x / total, reward, total)
	inhibit1_ = Expression(lambda x, total: x / total, inhibit1, total)
	inhibit2_ = Expression(lambda x, total: x / total, inhibit2, total)

	# TODO: Fix color propagation, once and for all
	reward_.output.color = 'green'
	inhibit1_.output.color = 'cyan'
	inhibit2_.output.color = 'violet'

	OSC2 = Oscilloscope('Intensity', channels=[reward_, inhibit1_, inhibit2_])
	waterfall = Waterfall('Waterfall', input=ch1, window_size=512, update_rate=20, history_size=50)

	layout = QGridLayout()
	layout.addWidget(OSC1.widget())
	layout.addWidget(Spec.widget())
	layout.addWidget(OSC2.widget())
	layout.addWidget(waterfall.widget(), 0, 1, 3, 1)

	reward = Threshold('reward', input=reward).passfail
	inhibit1 = Threshold('inhibit1', input=inhibit1, mode='decrease').passfail
	inhibit2 = Threshold('inhibit2', input=inhibit2, mode='decrease').passfail

	reward = Averager(reward)
	inhibit1 = Averager(inhibit1)
	inhibit2 = Averager(inhibit2)
	

	def update_qml(reward, inhibit1, inhibit2, total):
		brightness = (reward * 0.4 + inhibit1 * 0.3 + inhibit2 * 0.3)

		#volume = float(reward / inhibit1) / 0.045 - 1.0


		videoPlayer.setProperty('brightness', brightness)
		#videoPlayer.setProperty('volume', volume)

	foo = Expression(update_qml, reward, inhibit1, inhibit2, total)



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
		try:
			if hasattr(child, 'block'):
				child.block.updateGUI()
		#		pass
		except NameError:
			pass

guiTimer = QtCore.QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)

myApp.exec_()
sys.exit()
