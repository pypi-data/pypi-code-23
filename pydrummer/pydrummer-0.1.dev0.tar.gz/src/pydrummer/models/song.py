from pydrummer.models.clip import Clip


class Song():
    """A Song is a container for Clips.
    """

    def __init__(self):
        self.clips = []

    def add_clip(self, instruments, steps=16):
        clip = Clip(instruments=instruments, steps=steps)
        self.clips.append(clip)
