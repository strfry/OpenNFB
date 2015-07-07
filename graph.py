import numpy as np


class Block(object):
	def __init__(self):
		self.input = InputPort()
		self.output = OutputPort()
	pass

class FilterBlock(Block):
	pass


class InputPort(object):
	def __init__(self, block):
	pass

class OutputPort(object):
	pass

class Buffer(object):
    def __init__(self, size):
        self.data = np.zeros(size)
        self.newSamples = 0

    def


class Context(object):
	def __init__(self):
		self.connections = set()
        self.source_nodes = set()
        self.execution_order = []
		pass

	def connect(self, outport, inport):
		self.connections.add()

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



	def source_block(self):
		return self.source

	def process(self):
        for node in self.execution_order:
            node.process()






		pass

