from PySide import QtGui, QtCore
from PySide.phonon import Phonon

import sys

app = QtGui.QApplication(sys.argv)


source = Phonon.MediaSource("test.mp4")

vid = Phonon.VideoPlayer()
#vid  = Phonon.VideoWidget()
vid.load(source)
vid.play()
vid.show()

def set_stuff():
  import random
  #height = int(random.random() * 200)
  #vid.setFixedHeight(height)
  vid.videoWidget().setBrightness(-random.random())
  print vid.videoWidget().brightness()
  

timer = QtCore.QTimer()
timer.timeout.connect(set_stuff)
timer.start(200)

print dir(vid)

app.exec_()
