from flow import Block, Signal, Input

from traits.api import Bool, List, on_trait_change, Int, Float, CFloat, Enum, Trait, Str, Tuple

import socket, struct

import threading, time

CMD_ADD_CHANNEL = 1
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
        #self.socket_thread()

    @on_trait_change('channels[]')
    def channels_changed(self, object, name, old, new):
        #for idx, ch in new:
        #    self._add_channel(ch)
        pass


    # Add header and send to clients
    def _send_packet(self, packet):
        global client_socket
        if not client_socket: return

        header = b'\xce\xfa\xce\xfe'
        header += struct.pack('<i', 8 + len(packet))
        packet = header + packet

        packet += b'\n'

        #client_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        #self.client.send(packet)
        client_socket.send(packet)

        # Disable Nagle's algorithm
        #client_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

        #print ('sent packet', ':'.join(['%02x' % c for c in packet]))


    def _send_data(self, index, data):
        packet = bytes()
        packet += struct.pack('<i', CMD_CHANNEL_DATA)
        packet += struct.pack('<i', index)
        packet += struct.pack('<i', len(data))



        import random
        for sample in data:
            packet += struct.pack('<d', sample)
            packet += struct.pack('<d', (random.random()-0.1) * 10e-9)

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

        print ('add channel', packet)




    def socket_thread(self):
        import rt_thread
        nperiod = int(1.0 / 60 * 1000000000)
        ncomputation = nperiod // 10
        nconstraint = ncomputation * 2
        #rt_thread.set_realtime(nperiod, ncomputation, nconstraint)



        try:
            global client_socket
            if not client_socket:
                client_socket = main_socket.accept()[0]

            for idx, ch in enumerate(self.channels):
                self._add_channel(ch, idx+1)

            self._stop()
            self._start()

            sent_timestamp = self.channels[0].timestamp

            while True:
                ts = self.channels[0].timestamp
                if sent_timestamp < ts:
                    l = ts - sent_timestamp

                    sent_timestamp += l

                    newdata = self.channels[0].buffer[-l:]

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
