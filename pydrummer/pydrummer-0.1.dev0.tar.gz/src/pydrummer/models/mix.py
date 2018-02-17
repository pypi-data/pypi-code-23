from pydrummer.models.sound import Sound


class Mix(object):
    """A Mix is a single multi-sound pattern created by combing Sequences.

    A Mix is used for rhythm playback.

    TODO: Look into merging steps into one big wave file where notes can
    continue to play until they finish instead of cutting every sound off at
    each step
    """

    def __init__(self, steps):
        self.steps = steps
        self.sounds = [Sound()] * steps
        self.pattern = [0] * steps

    def merge(self, sequence):
        """ Merge notes from the given sequence into the mix

        If the pattern in the given sequence has a note with the value of zero
        we do nothing and move on to the next note. If the note is one we merge
        it into the mix. We either merge the note into an existing note by
        mixing the two sounds together or we copy it into an empty slot in our
        pattern.
        """
        for i in range(self.steps):
            if sequence.pattern[i] == 0:  # nothing to copy or mix
                continue
            if self.pattern[i] == 0:  # copy note
                self.pattern[i] = 1
                self.sounds[i] = Sound(sequence.sound.name, sequence.sound.file_path)
                self.sounds[i].name = sequence.sound.name
            else:  # mix notes together
                self.sounds[i].mix(sequence.sound)
                self.sounds[i].name = 'mix'

    def get_sounds(self):
        return self.sounds
