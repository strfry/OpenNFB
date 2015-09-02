import time
import sys, signal
import socket
import json

from bdf import BDFReader

from PyQt5.QtCore import QTimer, QCoreApplication

app = QCoreApplication(sys.argv)
signal.signal(signal.SIGINT, signal.SIG_DFL)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_packet(channels):
	data = json.dumps(channels)
	sock.sendto(data.encode('utf-8'), ('localhost', 8888))

filehandler = open(sys.argv[1], 'rb')
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
