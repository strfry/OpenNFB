class Context(object):
    instance = None

    def __init__(self):
        if self.instance:
            print 'Warning: Context instantiated more than once'

        self.instance = self

    # TODO: Singleton

    def set_flow(self, flow):
        pass

    def _analyze_latency(self):
        pass

    def _replay_history(self):
        pass

    def append_channel_data(self, data):
        pass

    def process(self):
        self.flow.process()

    def get_channel(self, name, **config):
        print 'get_channel', name