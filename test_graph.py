import unittest
import graph
import numpy as np



class GraphTest(unittest.TestCase):
    def setUp(self):
        self.context = graph.Context()

    def tearDown(self):
        pass

    def test_null_block_chain(self):
        channel1 = self.context.channel_source("Channel 1")

        null1 = graph.NullBlock()
        null2 = graph.NullBlock()
        null3 = graph.NullBlock()

        self.context.connect(channel1, null1.input)
        self.context.connect(null1.output, null2.input)
        self.context.connect(null2.output, null3.input)

        input = np.random.random(channel1.MAX_CHUNK_SIZE)

        channel1.append_data(input)

        self.context.process()

        assert input == null3.output.data

    def test_context(self):

        #source = graph.Source()
        #osc = graph.Oscilloscope()

        #self.context.connect(source.output, osc.input)

        print self
        

#unittest.main()