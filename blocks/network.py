
class UDPSource(Block):
    channel1 = Output()

    def init(self):
        self.channel1.sample_rate = 250.0
        self.channel1.color = 'orange'
        self.gr_block = blocks.udp_source(gr.sizeof_float*1, "127.0.0.1", 9999, 1472, True)
      

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
