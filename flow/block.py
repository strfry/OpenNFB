from .signal import Signal
from traits.api import HasTraits, Instance

class Input(Instance):
    def __init__(self, default=None):
        super(Input, self).__init__(Signal, input=True)

        self.default = default



class Block(HasTraits):
    def __init__(self, **config):
        # Register for trait events with the metadata 'input', our Input trait
        self.on_trait_event(self._input_trait_handler, '+input')

        self.inputs = set()

        super(Block, self).__init__(**config)

        self.last_timestamp = -1
        
        if hasattr(self, 'init'):
            self.init()


    def _input_trait_handler(self, object, name, old, new):
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
