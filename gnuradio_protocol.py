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

from PyQt4 import Qt, QtCore, QtGui
from gnuradio import blocks
from gnuradio import audio
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import fft
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import sip
import sys

import pyqtgraph as pg

#from blocks import BEServer, Threshold
import numpy as np
import scipy.signal

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

cnt = 0

import threading, time
import math

class InputDict(object):
    pass

class Input(object):
    """Attribute type for describing signal inputs of Blocks"""

    # A counter used to find out the order of declaration 
    order = 0

    def __init__(self, type=np.float32):
        self.order = Input.order
        Input.order += 1

        self.type = type

    """Create a copy from a class attribute for a specific Block instance"""
    def instantiate(self, block, name):
        new = Input(type=self.type)
        new.block = block
        new.name = name
        new.cls = self

        print ('Input.instantiate', self, block, name, new)

        return new


    def __getattr__(self, attrname):
        if 'block' not in self.__dict__:
            raise ValueError('getattr call on uninstantiated Input', self)
        
        if 'source' in self.__dict__:
            return getattr(self.source, attrname)

        raise AttributeError(self, 'Input \'%s\' of Block %s does not have attribute \'%s\', nor any sources'
            % (name, block, attrname))


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

    """Create a copy from a class attribute for a specific Block instance"""
    def instantiate(self, block, name):
        print ('Output.instantiate', self, block, name)
        new = Output(type=self.type)
        new.block = block
        new.name = name

        # Get the instance of the source object
        new.source = block._get_input_instance(self.source)


        return new

    def __getattr__(self, attrname):
        #print ('Output getattr', attrname, self.__dict__['block'])
        #if hasattr(self, attrname):
        #if object(self, attrname):
        #    print ('p3')
        #    return super(self).__getattr__(attrname)

        if hasattr(self.block, attrname):
            return getattr(self.block, attrname)

        source = self.__dict__['source']
        if source:
            return getattr(source, attrname)
        print ('p5')

        raise AttributeError('Output does not have attribute \'' + attrname +
            '\', nor any sources')

class Block(object):
    def _get_input_instance(self, input):
        if not input: return None

        for attr in dir(self):
            inp = getattr(self, attr)
            if type(inp) == Input and inp.cls == input:
                return inp

        raise AttributeError('Can not find %s in %s', (input, self))

    def __init__(self, *args, **kwargs):
        inputs = []
        outputs = []

        # Search block for inputs/outputs, add them to a list
        # Also replace the declaration with a copy (instance)
        for attrname in dir(self):
            attr = getattr(self, attrname)
            if type(attr) in (Input, Output):
                print self, 'found type ', attr, attrname
                #attr = copy.copy(attr)
                attr = attr.instantiate(self, attrname)
                print attr.name, attr.block
                setattr(self, attrname, attr)

                if type(attr) == Input:
                    inputs.append(attr)
                elif type(attr) == Output:
                    outputs.append(attr)
            
        inputs.sort(key=lambda x: x.order)
        outputs.sort(key=lambda x: x.order)

        for i in inputs:
            print ('Block', self, ' Input', i)

        for i in outputs:
            print ('Block', self, ' Output', i)

        print (self, len(args), len(inputs), inputs)
        if len(args) < len(inputs):
            raise ValueError('Not enough arguments for input')

        args = list(args)
        for i, input in enumerate(inputs):
            input.index = i
            source = args.pop(0)

            if isinstance(source, Block):
                source = source.output
                print ('Assign output', self, source)

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
        nyquist = self.input.sample_rate / 2.0
        Wp = [lo / nyquist, hi / nyquist]
        #Ws = [(lo - 1) / nyquist, (hi+1) / nyquist]
        #b, a = scipy.signal.iirdesign(Wp, Ws, 0.1, 60.0)
        b, a = scipy.signal.iirfilter(6, Wp, btype='bandpass',
            ftype='ellip', rp=0.1, rs=60.0)

        #self.gr_block = filter.iir_filter_ffd(a, b, oldstyle=False)
        self.gr_block = filter.iir_filter_ffd(b, a, oldstyle=False)

class NotchFilter(InOutBlock):
    def init(self, freq=50.0, mod=0.9):
        theta = 2 * np.pi * 50 / self.input.sample_rate
        zero = np.exp(np.array([1j, -1j]) * theta)
        pole = mod * zero

        a, b = np.poly(pole), np.poly(zero)
        #notch_ab = numpy.poly(zero), numpy.poly(pole)
        #notch_ab = scipy.signal.iirfilter(32, [30.0 / 125], btype='low')

        self.gr_block = filter.iir_filter_ffd(b, a, oldstyle=False)
        

class RMS(InOutBlock):
    def init(self, alpha=0.01):
        self.gr_block = blocks.rms_ff(alpha)


class DCBlock(InOutBlock):
    def init(self, taps=16):
        self.gr_block = filter.dc_blocker_ff(16, long_form=False)

class ExponentialAverage(InOutBlock):
    def init(self, lookback = 1.0):
        samples = length * self.input.sample_rate
        scale = 1.0 / samples
        self.gr_block = blocks.moving_average_ff(int(samples), scale)



    def general_work(self, input_items, output_items):
        print ('BarSpectrogram work', len(input_items[0]), output_items, input_items[0][0])

        self.gr_block.consume_each(1)
        self.gr_block.produce_each(1)

        output_items[0][0] = result

        self.buffer = input_items[0][-len(self.win):]
        return 0

class Oscilloscope(Block):
    input = Input()

    def init(self, history=512, autoscale=True):
        self.widget = pg.PlotWidget()
        self.widget.block = self

        self.gr_block.set_history(history)

        self.plot = self.widget.plot()
        self.plot.setPen(QtGui.QColor(self.input.color))
        #self.widget.setYRange(*self.yrange)

        self.widget.enableAutoRange('y', 0.95 if autoscale else False)

        self.buffer = []

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateGUI)
        self.timer.start(100)


    def general_work(self, input_items, output_items):
        #print ('Oscilloscope work', len(input_items[0]), output_items, input_items[0][0])

        # TODO: Make relative to update rate
        self.gr_block.consume_each(5)

        self.buffer = input_items[0]

        return 0


    def updateGUI(self):
        self.plot.setData(self.buffer)
        self.widget.update()

class BarGraph(Block):
    inputs = InputDict()

    def init(self):
        pass


class BarSpectrogram(Block):
    input = Input()


    def init(self, lo=0, hi=125, bins=256, yrange=750, ratio=False):
        self.widget = pg.PlotWidget()
        self.widget.setLabel('bottom', 'Frequency', units='Hz')

        self.bars = pg.BarGraphItem()

        self.win = np.hanning(bins)
        self.win = np.blackman(bins)
        #self.win = np.ones(bins)
        self.lo, self.hi = lo, hi
        self.ratio = ratio
        
        FS = self.input.sample_rate

        self.gr_block.set_history(bins)

        #num_bars = int(round((self.bins - 1) * (self.hi - self.lo) / FS))
        # This is total bullshit:
        num_bars = len(np.zeros(bins)[lo: hi])

        x = np.linspace(self.lo, self.hi, num_bars)

        self.bars = pg.BarGraphItem(x=x, height=range(num_bars), width=1.0)
        
        self.bars.setOpts(brushes=[pg.hsvColor(float(x) / num_bars) for x in range(num_bars)])
        self.widget.addItem(self.bars)

        # TODO: Better autoranging features
        #self.plot.enableAutoRange('xy', False)
        
        self.widget.setYRange(0, yrange)
        self.widget.enableAutoRange('y', 0.95)

        self.buffer = np.zeros(bins)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateGUI)
        self.timer.start(10)


    def general_work(self, input_items, output_items):
        #print ('BarSpectrogram work', len(input_items[0]), output_items, input_items[0][0])

        self.gr_block.consume_each(16)

        self.buffer = input_items[0][-len(self.win):]
        return 0

    def updateGUI(self):


        C = np.fft.rfft(self.buffer * self.win)
        C = abs(C)

        lo, hi = self.lo, self.hi
        data = C[lo : hi]

        if self.ratio:
            data = data / sum(C)

        self.bars.setOpts(height=data)

        #self.widget.setData(input_items[0])
        self.widget.update()
        

    def widget(self):
        return self.plot


class UDPSource(Block):
    channel1 = Output()

    def init(self):
        self.channel1.sample_rate = 250.0
        self.channel1.color = 'orange'
        self.gr_block = blocks.udp_source(gr.sizeof_float*1, "127.0.0.1", 9999, 1472, True)
        

#class FloatToShort(InOutBlock):
#    def init(self):
#        self.gr_block = 

class AudioSink(Block):
    input = Input()

    def init(self):
        self.gr_block = audio.sink(int(self.input.sample_rate), "", True)

import OSC

# TODO: Make an OSC Connection class that makes send objects
class OSCSend(Block):
    input = Input()

    def init(self, address, send_period=0.05):
        self.samples = int(send_period * self.input.sample_rate)

        self.client = OSC.OSCClient()
        self.client.connect(('127.0.0.1', 5510))   # connect to Faust
        self.address = address

        self.gr_block.set_history(self.samples)


    def general_work(self, input_items, output_items):
        print ('OSCSend work', len(input_items[0]), output_items, input_items[0])

        self.gr_block.consume_each(self.samples)

        oscmsg = OSC.OSCMessage()
        oscmsg.setAddress(self.address)
        val = input_items[0][self.samples-1]
        val = val / 6 * 200
        oscmsg.append(val)
        self.client.send(oscmsg)
        return 0


class Stream2Vector(Block):
    input = Input()
    output = Output(type=(np.float32, 256))

    def init(self, bins=256, framerate=2):
        self.num_samples = int(self.input.sample_rate / framerate)

        self.gr_block.set_history(bins)
        self.bins = bins

    def general_work(self, input_items, output_items):
        self.gr_block.consume_each(self.num_samples)

        print 'Stream2Vector work', len(input_items[0])

        #output_items[0][:self.bins] = input_items[0][-self.bins:]
        output_items[0][0] = input_items[0][-self.bins:]
        #self.gr_block.produce(0, self.bins)
        self.gr_block.produce(0, 1)

        return 0

class FFT(Block):
    input = Input()
    bins = Output()

    def init(self, bins=256):
        self.gr_block = fft.fft_vfc(256, forward=True, window=fft.window.blackmanharris(bins))

        
from blocks import Threshold


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

        # Signal Conditioning: DC Block and 50 Hz Notch Filter
        ch1 = NotchFilter(src.channel1)
        #ch1 = src.channel1
        #ch1 = NotchFilter(ch1, freq=100)
        ch1 = DCBlock(ch1)

        #ch1 = BandPass(ch1, 1, 40)

        #notched = NotchFilter(notched)
        #notched = NotchFilter(notched)
        alpha = BandPass(ch1, 8, 12)
        alpha.color = 'green'
        alpha = RMS(alpha, 0.02)
        #alpha = ExponentialAverage(alpha, 5.1)

        smr = BandPass(ch1, 9.5, 12.5)

        sigs = alpha, smr
        rmss = map(RMS, sigs)

        #threshold = Threshold(rmss[1], 'increase')
        #oscclient = OSCSend(threshold.ratio, '/0x00/filter')
        #oscclient = OSCSend(rmss[1], '/0x00/filter')


        audio = BandPass(ch1, 7, 12)
        audio = ch1

        #osci = Oscilloscope(rmss[1])
        #osci = Oscilloscope(threshold.ratio)
        spec = BarSpectrogram(ch1, lo=0, hi=127, bins=256)

        vec = Stream2Vector(ch1)
        fft = FFT(vec)
        waterfall = WaterfallLines(fft.bins)
        #fft = FFT(Stream2Vector(ch1))

        osci = Oscilloscope(ch1) 
        #self.top_layout.addWidget(waterfall.widget)
        waterfall.widget.show()

        self.top_layout.addWidget(osci.widget)


        audiosink = AudioSink(audio)

        hlayout = Qt.QHBoxLayout()
        hlayout.addWidget(osci.widget)
        #\hlayout.addWidget(threshold.widget)
        #widget = Qt.QWidget()
        #widget.addLayout(hlayout)

        #self.top_layout.addLayout(hlayout)

        self.top_layout.addWidget(spec.widget)

        visited = self.wireup(osci)
        #visited = self.wireup(osci0, visited)
        #visited = self.wireup(oscclient, visited)
#        visited = self.wireup(threshold, visited)
        visited = self.wireup(spec, visited)
        
        visited = self.wireup(waterfall, visited)
        


    def wireup(self, destination, visited=[]):
        print 'wireup', destination, visited
        if destination in visited: return visited

        visited = visited + [destination]

        for idx in dir(destination):
            inp = getattr(destination, idx)
            if type(inp) == Input:
                self.connect(inp.source.block.gr_block, inp.block.gr_block)
                return self.wireup(inp.source.block, visited)

        return visited

        
        

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
