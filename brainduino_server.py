import serial
from sys import argv
from string import Formatter
import socket

import json


tty_port = "/dev/tty.usbserial-A703X8ZG"

if len(argv) > 1:
    tty_port = argv[1]

timeout = 99

print "Trying to open serial port... ", tty_port,
ser = serial.Serial(port=tty_port, baudrate = 230400, timeout=timeout)
print "Success!"

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
#    print a
    if a == '\r' and len(buffer) == 15:
		parse(buffer)
		buffer = ""
    elif len(buffer) > 16:
      buffer = ""
    else:
    	buffer += a
