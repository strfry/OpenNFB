from flow import Block, Input

from traits.api import Str

class MPlayerControl(Block):
    from mplayer import Player

    enable = Input()

    def init(self, path):
        self.player = self.Player('-input default-bindings')
        self.player.loadfile(path)
        self.player.pause()
        self.player.frame_drop(2)
        self.playing = False

    def process(self):
        enable = self.enable.last

        if self.playing and not enable:
            self.playing = False
            self.player.pause()

        if not self.playing and enable:
            self.playing = True
            self.player.pause()
