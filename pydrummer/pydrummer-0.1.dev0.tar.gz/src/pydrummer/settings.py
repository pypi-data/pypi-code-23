class PlaybackSettings(object):
    def __init__(self, bpm, time_signature):
        self.beats_per_measure = time_signature[0]
        self.beat_unit = time_signature[1]
        self.bpm = bpm
