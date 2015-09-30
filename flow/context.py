from flow import Signal

class Context(object):
    instance = None

    def __init__(self):
        if self.instance:
            print('Warning: Context instantiated more than once')

        self.instance = self

        self.input_channels = {}

    # TODO: Singleton

    def _analyze_latency(self):
        pass

    def _replay_history(self):
        pass

    def clear_signals(self):
        for channel in self.input_channels.values():
            channel.clear_connections()

    def register_channel(self, idx, channel_name):
        self.input_channels[idx] = Signal(name=channel_name)

    def append_channel_data(self, idx, data):
        self.input_channels[idx].append(data)

    def get_channels(self):
        return list(self.input_channels.values())

    def process(self):
        #self.flow.process()
        # Go through input channels,
        
        for channel in self.input_channels.values():
            channel.process()
        pass

    def get_channel(self, idx, **config):
        channel = self.input_channels[idx]
        # TODO: Make a copy, do not overwrite config
        channel.trait_set(**config)
        
        return self.input_channels[name]