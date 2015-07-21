import numpy as np


class Block(object):
    def __init__(self):
        self.input = InputPort()
        self.output = OutputPort()
    pass

class FilterBlock(Block):
    pass


class NullBlock(Block):

    def process(self):
        source = self.input.port
        newdata = source.data[source.new_samples]

        self.output.append_data(newdata)



class InputPort(object):
    def __init__(self, buffer_size=250):
        self.input = None
        self.buffer_size = buffer_size

    def set_input(self, port):
        self.port = port
        port.set_buffer_size(self.buffer_size)

class OutputPort(object):
    MAX_CHUNK_SIZE = 250

    def __init__(self):
        self.data = np.zeros(self.MAX_CHUNK_SIZE)
        self.new_samples = 0

    def append_data(self, data):
        self.new_samples = len(data)
        self.data[self.new_samples:] = self.data[:-self.new_samples]
        self.data[:self.new_samples] = data

    def set_buffer_size(self, buffer_size):
        total_buffer = buffer_size + self.MAX_CHUNK_SIZE
        if len(self.data) < total_buffer:
            self.data.resize(total_buffer, refcheck=False)

class Buffer(object):
    def __init__(self, size):
        self.data = np.zeros(size)
        self.newSamples = 0



class Context(object):
    def __init__(self):
        self.connections = set()
        self.source_nodes = set()
        self.execution_order = []
        self.channel_sources = {}
        pass

    def connect(self, outport, inport):
        self.connections.add((outport, inport))

        self._build_execution_order()

    def _build_execution_order(self):
        self.execution_order = list(self.source_nodes)

        dependencies = {}

        for x, y in self.connections:
            if y not in dependencies:
                dependencies[y] = set()
            dependencies[y].add(x)


        while len(dependencies) > len(self.execution_order):
            added = False
            for target, sources in dependencies:
                if sources.issubset(self.execution_order):
                    self.execution_order.append(target)
                    added = True

            if not added:
                raise "Can not resolve dependencies, maybe there is a cycle in the graph?"


    def channel_source(self, channel_name):
        if channel_name not in self.channel_sources:
            self.channel_sources[channel_name] = OutputPort()
        return self.channel_sources[channel_name]

    def source_block(self):
        return self.source

    def process(self):
        for node in self.execution_order:
            node.process()






        pass

