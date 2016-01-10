from open_bci_v3 import OpenBCIBoard
import sys, signal
import socket
import json
import struct

#app = QCoreApplication(sys.argv)
#signal.signal(signal.SIGINT, signal.SIG_DFL)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ttyPath = '/dev/ttyUSB0'
if len(sys.argv) > 1:
  ttyPath = sys.argv[1]

last_packet = 0


def send_packet(packet):
  global last_packet

  expected = (last_packet + 1) % 256

  if packet.id != expected:
  	print 'lost packet', expected

  last_packet = packet.id


  data = json.dumps(packet.channel_data)
  sock.sendto(data.encode('utf-8'), ('localhost', 8888))
  data = struct.pack('=f', packet.channel_data[0] * 0.022351744455307063)
  sock.sendto(data, ('localhost', 9999))

board = OpenBCIBoard(ttyPath, scaled_output=False)
board.print_register_settings()
board.start_streaming(send_packet)
