import serial
from sys import argv
from string import Formatter
import socket

import json


tty_port = "/dev/tty.usbserial-A703X8ZG"

if len(argv) > 1:
    tty_port = argv[1]

timeout = 99

ser = serial.Serial(port=tty_port, baudrate = 230400, timeout=timeout)

buffer = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_packet(channels):
	channels.extend([0, 0, 0, 0]) 
	data = json.dumps(channels)
	sock.sendto(data, ('localhost', 8888))


def parse(buf):
	values = buf.split('\t')
	data = [int(x, 16) for x in values]
	send_packet(data)
	print data, values

while True:
    a = ser.read()

    if a == '\r':
		parse(buffer)
		buffer = ""
    else:
    	buffer += a
