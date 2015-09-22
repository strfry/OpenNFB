from open_bci_v3 import OpenBCIBoard
import sys, signal
import socket
import json

#app = QCoreApplication(sys.argv)
#signal.signal(signal.SIGINT, signal.SIG_DFL)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ttyPath = '/dev/ttyUSB0'
if len(sys.argv) > 1:
  ttyPath = sys.argv[1]

def send_packet(packet):
  data = json.dumps(packet.channel_data)
  sock.sendto(data.encode('utf-8'), ('localhost', 8888))
  sock.sendto(data.encode('utf-8'), ('localhost', 9999))

board = OpenBCIBoard(ttyPath, scaled_output=False)
board.print_register_settings()
board.start_streaming(send_packet)
