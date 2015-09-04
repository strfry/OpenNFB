
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

	smr = BandPass(11.5, 14.5, input=ch1)
	smr = Averager(RMS(smr))

	beta = BandPass(23, 32, input=ch1)
	beta = Averager(RMS(beta))

	theta = BandPass(2, 6, input=ch1)
	theta = Averager(RMS(theta))

	total = DCBlock(RMS(ch1)).dc

	#total_rms = Averager(RMS(ch1))

	#smr = Expression(lambda x, y: x / y, smr, total_rms)
	smr.output.color = 'green'
	beta.output.color = 'blue'
	theta.output.color = 'violet'

	smr_ = Expression(lambda x, total: x / total, smr, total)
	beta_ = Expression(lambda x, total: x / total, beta, total)
	theta_ = Expression(lambda x, total: x / total, theta, total)

	OSC2 = Oscilloscope('Intensity', channels=[smr_, beta_, theta_])
	waterfall = Waterfall('Waterfall', input=ch1, window_size=1024, update_rate=50, history_size=50)

	layout = QGridLayout()
	layout.addWidget(OSC1.widget())
	layout.addWidget(Spec.widget())
	layout.addWidget(OSC2.widget())
	layout.addWidget(waterfall.widget(), 0, 1, 3, 1)

	

	def update_qml(smr, beta, theta, total):
		bias = 0.3
		factor = 1

		# Very important to cast to float here, Qt silently ignores numpy types
		
		# Beta 10-40, Target 1-10
		brightness = float(1.0 - beta / 10)
		#brightness = float(smr / beta) / 0.035 - 1.0
		brightness = float(smr / total * 1000)

		volume = float(smr / beta) / 0.045 - 1.0


		videoPlayer.setProperty('brightness', brightness)
		videoPlayer.setProperty('volume', volume)

		global counter
		#if not counter: counter = 0
		counter += 1
		if counter > 50:
			counter = 0
			videoPlayer.setProperty('speed', brightness)
			print ('beta ', beta/total, 'smr ', smr/total, 'theta ', theta/total, 'total power', total)

		return 0.0

	foo = Expression(update_qml, smr, beta, theta, total)



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
