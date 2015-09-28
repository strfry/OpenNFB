from flow import Block, Signal, Input

from traits.api import Bool, List, on_trait_change, Int, Float, CFloat, Enum, Trait, Str, Tuple

import socket, struct

import threading

CMD_ADD_CHANNEL = 1
CMD_CHANNEL_DATA = 5

main_socket = None
client_socket = None

class BEServer(Block):

    channels = List(Input())

    def init(self, channels):
        #self.client = None

        #self.socket = socket.socket()
        #self.socket.bind(('', 2666))
        #self.socket.listen(1)

        global main_socket
        if not main_socket:
            main_socket = socket.socket()
            main_socket.setsockopt(socket.SOL_TCP, socket.SO_REUSEADDR, 1)
            main_socket.bind(('', 2666))
            main_socket.listen(1)

        self.channels = list(channels.values())


        threading.Thread(target=self.socket_thread).start()

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

        #self.client.send(packet)
        client_socket.send(packet)


    def _send_data(self, index, data):
        packet = bytes()
        packet += struct.pack('<i', CMD_CHANNEL_DATA)
        packet += struct.pack('<i', index)
        packet += struct.pack('<i', len(data))


        import random
        for sample in data:
            #packet += struct.pack('<d', sample)
            packet += struct.pack('<d', (random.random()-0.1) * 10e-9)

        self._send_packet(packet)


    def _add_channel(self, channel, index):
        packet = bytes()
        packet += struct.pack('<i', CMD_ADD_CHANNEL)
        packet += struct.pack('<i', index)
        packet += struct.pack('<d', channel.sample_rate)

        name = 'Channel %d' % (index + 1)

        if hasattr(channel, 'name'):
            name = channel.name

        name = name.encode('utf-8')

        packet += struct.pack('<i', len(name) + 1)
        packet += name + b'\0'


        self._send_packet(packet)




    def socket_thread(self):
        global client_socket
        if not client_socket:
            #client_socket = self.socket.accept()[0]
            client_socket = main_socket.accept()[0]

        for idx, ch in enumerate(self.channels):
            self._add_channel(ch, idx)

        sent_timestamp = self.channels[0].timestamp

        while True:
            ts = self.channels[0].timestamp
            if sent_timestamp < ts:
                l = ts - sent_timestamp

                newdata = self.channels[0].buffer[-l:]

                self._send_data(0, newdata)





                # print('send thread ts %d to %d' % (sent_timestamp, ts))
                sent_timestamp = ts



            import time
            time.sleep(0)

    def __del__(self):
        print ('BEServer closing socket...')

        global main_socket, client_socket

        if main_socket: main_socket.close()
        if client_socket: client_socket.close()



    def process(self):
        pass
