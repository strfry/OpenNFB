class Block(object):
    def __init__(self, **configs):
        pass

    def define_input(self, name):
        pass

    def __getattr__(self, attr):
        print 'getattr', value, __dict__[attr]
        return __dict__[attr]

    def __setattr__(self, attr, value):
        print '__setattr__', attr, value

class Flow(Block):
    pass