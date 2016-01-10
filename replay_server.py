import time
import sys, signal, struct
import socket
import json

from bdf import BDFReader, WAVReader

from pyqtgraph import QtCore, QtGui

signal.signal(signal.SIGINT, signal.SIG_DFL)
app = QtCore.QCoreApplication(sys.argv)
#app = QtGui.QApplication(sys.argv)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_packet(channels):
	data = json.dumps(channels)
	sock.sendto(data.encode('utf-8'), ('localhost', 8888))
	data = struct.pack('=f', channels[0] * 0.022351744455307063)
	sock.sendto(data, ('localhost', 9999))

filename = sys.argv[1]
filehandler = open(filename, 'rb')

if filename.lower().endswith('.wav'):
	bdf = WAVReader(filehandler)
else:
	bdf = BDFReader(filehandler)

def handle_timeout():
    packet = bdf.readPacket()
    if packet:
    	send_packet(packet)
    else:
    	app.quit()

timer = QtCore.QTimer()
timer.timeout.connect(handle_timeout)
#timer.start(1000 / 250)
timer.start(3)

app.exec_()
