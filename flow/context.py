class Context(object):
    def __init__(self):
        print instance

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