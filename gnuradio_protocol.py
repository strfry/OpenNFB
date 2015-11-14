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

from PyQt4 import Qt, QtGui
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

import pyqtgraph as pg

from blocks import BEServer, Threshold
import numpy as np
import scipy.signal

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

cnt = 0

import threading, time
import math

class Input(object):
    """Attribute type for describing signal inputs of Blocks"""

    # A counter used to find out the order of declaration 
    order = 0

    def __init__(self, type=np.float32):
        self.order = Input.order
        Input.order += 1

        self.type = type

    def __getattr__(self, attrname):
        if hasattr(self, attrname):
            return __getattribute__(self, attrname)

        if self.source:
            return getattr(self.source, attrname)

        raise AttributeError('Input does not have attribute \'' + attrname +
            '\', nor any sources')


class Output(object):
    """Attribute type for describing signal outputs of Blocks"""

    # A counter used to find out the order of declaration 
    order = 0

    def __init__(self, source=None, type=np.float32):
        print ('Output init', source, type)
        self.order = Input.order
        Output.order += 1

        self.source = source
        self.type = type


    def __getattr__(self, attrname):
        print ('p1')
        #if hasattr(self, attrname):
        if attrname in self.__dict__:
            return self.__dict__[attrname]


        print ('p2')
        source = self.__dict__['source']

        print ('p3')

        print ('Output getattr', attrname, source)
        print ('p4')

        if source:
            return getattr(source, attrname)
        print ('p5')

        raise AttributeError('Output does not have attribute \'' + attrname +
            '\', nor any sources')


class Block(object):
    def __init__(self, *args, **kwargs):
        inputs = []
        outputs = []

        for attrname in dir(self):
            attr = getattr(self, attrname)
            if type(attr) == Input:
                inputs.append(attr)
            elif type(attr) == Output:
                outputs.append(attr)

        inputs.sort(key=lambda x: x.order)
        outputs.sort(key=lambda x: x.order)

        if len(args) < len(inputs):
            raise ValueError('Not enough arguments for input')

        args = list(args)
        for i, input in enumerate(inputs):
            input.index = i
            source = args.pop(0)

            if isinstance(source, Block):
                source = source.output

            input.source = source

        for i, output in enumerate(outputs):
            output.index = i

        input_types = [x.type for x in inputs]
        output_types = [x.type for x in outputs]

        name = self.__class__.__name__

        if hasattr(self, 'general_work'):
            self.gr_block = gr.basic_block(name, input_types, output_types)
            self.gr_block.general_work = self.general_work

        self.init(*args, **kwargs)

        assert hasattr(self, 'gr_block')

class InOutBlock(Block):
    "A base class for the default case of a block with input and one output"
    input = Input()
    output = Output(input)


class BandPass(InOutBlock):    
    def init(self, lo, hi): 
        Wn = [lo / self.input.sample_rate / 2, hi / self.input.sample_rate / 2]
        filter_ab = scipy.signal.iirfilter(8, Wn, btype='bandpass')

        self.gr_block = filter.iir_filter_ffd(filter_ab[1], filter_ab[0], oldstyle=False)


class Oscilloscope(Block):
    input = Input()

    def init(self, history=512, autoscale=True):
        name = 'Oscilloscope'
        self.widget = pg.PlotWidget(title=name)
        self.widget.block = self

        self.name = name

        self.gr_block.set_history(history)

        self.plot = self.widget.plot()
        self.plot.setPen(QtGui.QColor(self.input.color))
        #self.widget.setYRange(*self.yrange)

        self.widget.enableAutoRange('y', 0.95 if autoscale else False)


    def general_work(self, input_items, output_items):
        print ('Oscilloscope work', len(input_items[0]), output_items, input_items[0][0])

        self.gr_block.consume_each(50)

        self.plot.setData(input_items[0])
        self.widget.update()

        return 0


    def updateGUI(self):
        for channel in self.plots:
            plot = self.plots[channel]
            plot.setData(channel.buffer)

class UDPSource(Block):
    channel1 = Output()

    def init(self):
        self.channel1.sample_rate = 250.0
        self.channel1.color = 'orange'
        self.gr_block = blocks.udp_source(gr.sizeof_float*1, "127.0.0.1", 9999, 1472, True)
        

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
        # Blocks
        ##################################################
        self.qtgui_sink_x_0 = qtgui.sink_f(
        	256, #fftsize
        	firdes.WIN_HANN, #wintype
        	50, #fc
        	250, #bw
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

        src = UDPSource()
        bp = BandPass(src.channel1, 0.0000001, 0.0002)
        osc = Oscilloscope(bp)

        self.top_layout.addWidget(osc.widget)


        self.connect(src.gr_block, bp.gr_block, osc.gr_block)
        #self.connect(src.gr_block, osc.gr_block)


        # Signal Conditioning: DC Block and 50 Hz Notch Filter
        #dc_blocker = filter.dc_blocker_ff(16, long_form=False)
        #self.connect((test_source, 0), (dc_blocker, 0))

        theta = 2 * np.pi * 50 / 250
        zero = np.exp(np.array([1j, -1j]) * theta)
        pole = 0.999 * zero

        #notch_ab = numpy.poly(pole), numpy.poly(zero)
        #notch_ab = numpy.poly(zero), numpy.poly(pole)
        #notch_ab = scipy.signal.iirfilter(32, [30.0 / 125], btype='low')

        #notch_filter = filter.iir_filter_ffd(notch_ab[0], notch_ab[1], oldstyle=False)
        
        #total_rms = blocks.rms_ff(alpha=0.2)
        
        #threshold1 = Threshold()
        
        #self.connect((total_rms, 0), (self.qtgui_sink_x_0, 0))


        #self.beserver = BEServer()
        

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
