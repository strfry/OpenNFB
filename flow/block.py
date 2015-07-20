class Input(object):
    def __init__(self, block, name):
        self.name = name 
        self.block = block
        self.source = None

    def assign_source(self, output):
        if self.source:
            self.source.disconnect(self)

        output.connect(self.block)
        self.source = output
        pass


class Block(object):
    def __init__(self, **config):
        self._inputs = {}

        pass

    def define_input(self, name):
        self._inputs[name] = Input(self, name)
        pass

    def define_input_array(self, name, num):
        self._inputs[name] = Input(self, name)
        pass

    def define_config(self, name, default):
        self.__setattr__(name, default)


class Flow(Block):
    pass