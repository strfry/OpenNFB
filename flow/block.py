from .signal import Signal
from traits.api import HasTraits, Disallow, TraitType, on_trait_change

class Input(TraitType):
    def __init__(self, default=None):
        super(Input, self).__init__(default, input=True)

        self.default = default

    def info(self):
        return 'a Signal or output Block instance'

    def validate(self, object, name, value):
        if isinstance(object, Block) and not hasattr(object, 'inputs'):
            raise Exception("Input trait can't be assigned before Block.__init__")

        if isinstance(value, Block):
            if hasattr(value, 'output'):
                value = value.output

        if not isinstance(value, Signal):
            self.error(object, name, value)

        return value


class Block(HasTraits):
    #_ = Disallow

    def __init__(self, *args, **config):
        self.inputs = set()

        super(Block, self).__init__(**config)

        self.last_timestamp = -1
        
        if hasattr(self, 'init'):
            self.init(*args)

    def __del__(self):
        print ('Block ', self, 'deleted')


    # Register for trait events with the metadata 'input', our Input trait
    @on_trait_change('+input')
    def _input_trait_handler(self, object, name, old, new):
        print ('assigned channel', new, 'to', object)
        if old:
            old._disconnect(self)
            self.inputs.remove(old)

        new._connect(self)
        self.inputs.add(new)

    def _signal_ready(self, signal):
        if signal.timestamp > self.last_timestamp:
            self.ready_inputs = set([signal])
            self.last_timestamp = signal.timestamp
        else:
            self.ready_inputs.add(signal)

        if self.ready_inputs == self.inputs:
            self.process()
