#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Tue Oct  6 22:40:10 2015
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import sip
import sys

from blocks import BEServer
import numpy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

cnt = 0

import threading, time
import math

class TestSource(gr.basic_block):
    def __init__(self):
        super(TestSource, self).__init__('TestSource', [], [numpy.float32])

        self.buffer = []
        #self.set_auto_consume(False)

        threading.Thread(target=self.thread_worker).start()



    def thread_worker(self):
        print ('Starting Thread')
        while True:
            global cnt
            cnt += 1
            val = (math.sin(cnt / 250.0) + 1 )
            self.buffer.append(val)
            time.sleep(1.0 / 250)

    def general_work(self, input_items, output_items):
        #print ('TestSource', input_items, output_items)

        out = output_items[0]
        
        max_items = len(out)
        n_items = len(self.buffer[:max_items])

        out[:n_items] = self.buffer[:n_items]

        #self.produce(0, len(self.buffer))
        self.buffer = []

        return n_items


class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
        try:
             self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
             pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 250

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_sink_x_0 = qtgui.sink_f(
        	32, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	50, #fc
        	samp_rate, #bw
        	"", #name
        	True, #plotfreq
        	True, #plotwaterfall
        	True, #plottime
        	True, #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/100)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        
        #self.qtgui_sink_x_0.enable_rf_freq(False)
        
        
          
        #self.blocks_udp_source_0 = blocks.udp_source(gr.sizeof_float*1, "127.0.0.1", 9999, 1472, True)
        #self.blocks_udp_source_0 = TestSource()
        test_source = TestSource()
        #self.blocks_throttle_0 = blocks.throttle(gr.sizeof_int*1, samp_rate,True)
        self.band_pass_filter_0 = filter.fir_filter_fff(1, firdes.band_pass(
        	1, samp_rate, 1, 30, 1, firdes.WIN_HAMMING, 6.76))

        self.beserver = BEServer()

        ##################################################
        # Connections
        ##################################################
        #self.connect((self.band_pass_filter_0, 0), (self.qtgui_sink_x_0, 0))    
        #self.connect((self.blocks_throttle_0, 0), (self.band_pass_filter_0, 0))    
        #self.connect((self.blocks_udp_source_0, 0), (self.blocks_throttle_0, 0))    
        #self.connect((self.blocks_udp_source_0, 0), (self.band_pass_filter_0, 0))    
        #self.connect((self.band_pass_filter_0, 0), (self.beserver, 0))

        self.connect((test_source, 0), (self.beserver, 0))
        self.connect((test_source, 0), (self.qtgui_sink_x_0, 0))
        #self.connect((self.blocks_udp_source_0, 0), (self.beserver, 0))
        #self.connect((self.blocks_udp_source_0, 0), (self.qtgui_sink_x_0, 0))    



if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = top_block()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        #tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None  # to clean up Qt widgets
