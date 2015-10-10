
from gnuradio import gr

import numpy
import threading
import time
import socket
import struct


main_socket = None
client_socket = None

CMD_ADD_CHANNEL = 1
CMD_CHANNEL_DATA = 5
CMD_START = 6
CMD_STOP = 8


class BEServer(gr.basic_block):
    def __init__(self):
        super(BEServer, self).__init__('BEServer', [numpy.float32], [])
        self.send_buffer = []

        self.init()

    def general_work(self, input_items, output_items):
        # No queueing up stuff
        if client_socket:
            self.send_buffer.extend(input_items[0])

        self.consume(0, len(input_items[0]))

        return 0
    
    def init(self):
        global main_socket
        if not main_socket:
            main_socket = socket.socket()
            main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Disable Nagle's algorithm
            main_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            main_socket.bind(('', 2666))
            main_socket.listen(1)

        
        threading.Thread(target=self.socket_thread).start()

    # Add header and send to clients
    def _send_packet(self, packet):
        global client_socket
        if not client_socket: return

        header = b'\xce\xfa\xce\xfe'
        header += struct.pack('<i', 8 + len(packet))
        packet = header + packet

        packet += b'\n'

        client_socket.send(packet)

        #print ('sent packet', ':'.join(['%02x' % ord(c) for c in packet]))


    def _send_data(self, index, data):
        packet = bytes()
        packet += struct.pack('<i', CMD_CHANNEL_DATA)
        packet += struct.pack('<i', index)
        packet += struct.pack('<i', len(data))

        for sample in data:
            packet += struct.pack('<d', sample)

        self._send_packet(packet)


    def _start(self):
        packet = struct.pack('<i', CMD_START)
        self._send_packet(packet)

    def _stop(self):
        packet = struct.pack('<i', CMD_STOP)
        self._send_packet(packet)


    def _add_channel(self, sample_rate, index):
        packet = bytes()
        packet += struct.pack('<i', CMD_ADD_CHANNEL)
        packet += struct.pack('<i', index)
        packet += struct.pack('<d', sample_rate)

        name = 'Channel %d' % (index + 1)

        #if hasattr(channel, 'name'):
        #    name = channel.name

        name = name.encode('utf-8') + b'\0'

        packet += struct.pack('<i', len(name))
        packet += name


        self._send_packet(packet)

        #print ('add channel', packet)


    def socket_thread(self):
        #import rt_thread
        nperiod = int(1.0 / 60 * 1000000000)
        ncomputation = nperiod // 10
        nconstraint = ncomputation * 2
        #rt_thread.set_realtime(nperiod, ncomputation, nconstraint)


        #try:
        if True:
            global client_socket
            if not client_socket:
                client_socket = main_socket.accept()[0]

            #for idx, ch in enumerate(self.channels):
            #    self._add_channel(ch, idx+1)
            self._add_channel(250.0, 1)

            self._stop()
            self._start()

            #sent_timestamp = self.channels[0].timestamp

            while True:
                if len(self.send_buffer):
                    newdata = self.send_buffer[:]
                    self.send_buffer = []

                    self._send_data(1, newdata)

                time.sleep(0.05)
                #rt_thread.thread_yield()
        #except BrokenPipeError:
        #    client_socket = None
        #    self.socket_thread()

    def __del__(self):
        print ('BEServer closing socket...')

        global main_socket, client_socket

        if main_socket: main_socket.close()
        if client_socket: client_socket.close()



    def process(self):
        pass

