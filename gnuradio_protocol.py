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

from blocks import BEServer, Threshold
import numpy
import scipy.signal

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

class TestSink(gr.sync_block):
    def __init__(self):
        super(TestSink, self).__init__('TestSink', [numpy.float32], [])

        self.cnt = 0

    def work(self, input_items, output_items):
        for i in input_items[0]:
            self.cnt += 1
            if self.cnt > 250:
                print (i)
                self.cnt = 0

        return len(input_items[0])






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
        	256, #fftsize
        	firdes.WIN_HANN, #wintype
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
          
        #test_source = TestSource()
        test_source = blocks.udp_source(gr.sizeof_float*1, "127.0.0.1", 9999, 1472, True)


        # Signal Conditioning: DC Block and 50 Hz Notch Filter
        dc_blocker = filter.dc_blocker_ff(16, long_form=False)
        self.connect((test_source, 0), (dc_blocker, 0))

        theta = 2 * numpy.pi * 50 / 250
        zero = numpy.exp(numpy.array([1j, -1j]) * theta)
        pole = 0.999 * zero

        #notch_ab = numpy.poly(pole), numpy.poly(zero)
        #notch_ab = numpy.poly(zero), numpy.poly(pole)
        notch_ab = scipy.signal.iirfilter(32, [30.0 / 125], btype='low')

        notch_filter = filter.iir_filter_ffd(notch_ab[0], notch_ab[1], oldstyle=False)
        self.connect((dc_blocker, 0), (notch_filter, 0))

        #test_sink = TestSink()
        #self.connect((notch_filter, 0), (test_sink, 0))

        total_rms = blocks.rms_ff(alpha=0.2)
        self.connect((notch_filter, 0), (total_rms, 0))

        threshold1 = Threshold()
        self.connect((total_rms, 0), (threshold1, 0))
        #self.connect((total_rms, 0), (self.qtgui_sink_x_0, 0))

        self.connect((threshold1, 0), (blocks.null_sink(4), 0))
        self.connect((threshold1, 1), (blocks.null_sink(1), 0))
        self.connect((threshold1, 2), (self.qtgui_sink_x_0, 0))

        self.beserver = BEServer()
        self.connect((threshold1, 2), (self.beserver, 0))



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
