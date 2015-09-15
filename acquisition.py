from pyqtgraph import QtCore

import socket

class UDPThread(QtCore.QThread):
  newPacket = QtCore.pyqtSignal(object)
  
  def __init__(self, port=8888):
    super(UDPThread, self).__init__()

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.bind(('127.0.0.1', port))

  def run(self):
    while True:
      data, addr = self.socket.recvfrom(1024)
      data = eval(data)
      self.newPacket.emit(eval(str(data)))
      #QtGui.QApplication.instance().processEvents()
