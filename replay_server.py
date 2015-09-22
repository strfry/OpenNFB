import time
import sys, signal
import socket
import json

from bdf import BDFReader, WAVReader

from PyQt5.QtCore import QTimer, QCoreApplication

signal.signal(signal.SIGINT, signal.SIG_DFL)
app = QCoreApplication(sys.argv)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_packet(channels):
	data = json.dumps(channels)
	sock.sendto(data.encode('utf-8'), ('localhost', 8888))
	sock.sendto(data.encode('utf-8'), ('localhost', 9999))

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

timer = QTimer()
timer.timeout.connect(handle_timeout)
timer.start(1000 / 250)

app.exec_()
