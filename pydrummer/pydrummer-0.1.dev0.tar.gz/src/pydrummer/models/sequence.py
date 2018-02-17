from pydrummer.models.sound import Sound


class Sequence(object):
    """A Sequence is a series of notes defined by a pattern and a Sound.

    A pattern is an array of zeros and ones and has a length equal to the
    number of steps in our playback window.
    """

    def __init__(self, name, fpath, steps):
        self.name = name
        self.sound = Sound(name, fpath)
        self.steps = steps
        self.pattern = [0] * steps

    def set_pattern(self, pattern):
        """Set the pattern.

        If the length of given pattern is smaller than the length of the pattern
        in our Sequence, loop throught it again an continue setting elements
        until you reach the end.
        """
        for i in range(len(self.pattern)):
            self.pattern[i] = pattern[i % len(pattern)]

    def get_sounds(self):
        sounds = []
        for i in range(len(self.pattern)):
            if self.pattern[i] == 1:
                sounds.append(self.sound)
            else:
                sounds.append(Sound())
        return sounds
