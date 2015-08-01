from pyqtgraph import QtCore, QtGui
from open_bci_v3 import OpenBCIBoard
from bdf import BDFReader

class OpenBCIThread(QtCore.QThread):
  newPacket = QtCore.Signal(object)
  
  def __init__(self, ttyPath = '/dev/ttyUSB0'):
    super(OpenBCIThread, self).__init__()
    
    self.board = OpenBCIBoard(ttyPath, scaled_output=False)

  def handlePacket(self, sample):
    self.newPacket.emit(sample.channel_data)
    QtGui.QApplication.instance().processEvents()
    
  def run(self):
    try:
      self.board.print_register_settings()
      self.board.start_streaming(self.handlePacket)

    # Important workaround for OSX: If the input is not kept on being read, the whole (input sub-)system freezes
    except Exception as e:
      print ("Exception", e)
      while True:
        self.board.ser.read()

import socket

class UDPThread(QtCore.QThread):
  newPacket = QtCore.Signal(object)
  
  def __init__(self, port=8888):
    super(UDPThread, self).__init__()

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.bind(('127.0.0.1', port))

  def run(self):
    while True:
      data, addr = self.socket.recvfrom(1024)
      data = eval(data)
      self.newPacket.emit(eval(str(data)))
      QtGui.QApplication.instance().processEvents()

    
class BDFThread(QtCore.QThread):
  newPacket = QtCore.Signal(object)

  def __init__(self, filename):
    super(BDFThread, self).__init__()
    self.bdf = BDFReader(open(filename, 'rb'))

  def emitPacket(self):
    packet =  self.bdf.readPacket()
    if packet:
        self.newPacket.emit(packet)
    else:
        self.quit()

  def run(self):
    timer = QtCore.QTimer()
    timer.timeout.connect(self.emitPacket)
    timer.start(1000 / 250)

    self.exec_()


def Device(object):
    def __init__(self, driver='OpenBCI', ):
        pass
