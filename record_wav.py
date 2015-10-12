from acquisition import UDPThread
import sys
import signal
import wave
import struct

from pyqtgraph import QtCore

app = QtCore.QCoreApplication(sys.argv)
signal.signal(signal.SIGINT, signal.SIG_DFL)

source = UDPThread(port=9999)


f = wave.open(sys.argv[1], 'w')
f.setnchannels(8)
f.setsampwidth(3)
f.setframerate(250)


def handle_packet(packet):
	for ch in packet:
		data = struct.pack('<i', ch)
		f.writeframes(data[1:])
		#print (len(data[:1]))


	#print (data)


source.newPacket.connect(handle_packet)
source.start()

app.exec_()
