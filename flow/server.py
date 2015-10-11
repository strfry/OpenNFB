from flow import Block, Signal, Input

from traits.api import Bool, List, on_trait_change, Int, Float, CFloat, Enum, Trait, Str, Tuple

import socket, struct

import threading, time

CMD_ADD_CHANNEL = 1
CMD_REMOVE_CHANNEL = 2
CMD_CHANNEL_DATA = 5
CMD_START = 6
CMD_STOP = 8

main_socket = None
client_socket = None

class BEServer(Block):

    channels = List(Input())

    def init(self, channels):
        global main_socket
        if not main_socket:
            main_socket = socket.socket()
            main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Disable Nagle's algorithm
            main_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            main_socket.bind(('', 2666))
            main_socket.listen(1)

        self.channels = list(channels.values())


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

    def _send_data(self, index, data):

        print ('send_data to', index, data)


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


    def _add_channel(self, channel, index):
        packet = bytes()
        packet += struct.pack('<i', CMD_ADD_CHANNEL)
        packet += struct.pack('<i', index)
        packet += struct.pack('<d', channel.sample_rate)

        name = 'Channel %d' % (index + 1)

        if hasattr(channel, 'name'):
            name = channel.name

        name = name.encode('utf-8') + b'\0'

        packet += struct.pack('<i', len(name))
        packet += name


        self._send_packet(packet)

        print ('add channel', name, index)

    def _remove_channel(self, index):
        packet = bytes()
        packet += struct.pack('<i', CMD_REMOVE_CHANNEL)
        packet += struct.pack('<i', index)

        self._send_packet(packet)





    def socket_thread(self):
        try:
            global client_socket
            if not client_socket:
                client_socket = main_socket.accept()[0]


            self._stop()

            #for i in range(32):
            #    self._remove_channel(i)

            for idx, ch in enumerate(self.channels):
                self._add_channel(ch, idx)

            self._start()

            sent_timestamp = self.channels[0].timestamp

            while True:
                ts = self.channels[0].timestamp
                if sent_timestamp < ts:
                    l = ts - sent_timestamp
                    #l = min(l, 2)

                    sent_timestamp += l

                    newdata = self.channels[3].buffer[-l:]

                    self._send_data(1, newdata)

                time.sleep(0)
                #rt_thread.thread_yield()
        except BrokenPipeError:
            client_socket = None
            self.socket_thread()

    def __del__(self):
        print ('BEServer closing socket...')

        global main_socket, client_socket

        if main_socket: main_socket.close()
        if client_socket: client_socket.close()



    def process(self):
        pass
