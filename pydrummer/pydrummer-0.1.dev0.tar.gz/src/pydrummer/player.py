import sounddevice
import itertools
import time

from pydrummer.settings import PlaybackSettings

SECONDS_PER_MIN = 60.0
MIN_STEP_TIME = 0.01    # TODO: Figure out a way to not have to cut off notes at the
                        # beginning of the next step. This is will make it so we don't
                        # hit this minimum so often, which will give us a less choppy
                        # sound.


class Player(object):
    def __init__(self):
        self.settings = PlaybackSettings(bpm=120, time_signature=(4,4))

    def play(self, song=None, clip=None, sequence=None, sound=None, loops=-1):
        if sound:
            self.play_sound(sound=sound, blocking=True)
            print('')
        if sequence:
            self.play_sequence(sequence=sequence, loops=loops)
        if clip:
            self.play_clip(clip=clip, loops=loops)
        if song:
            self.play_song(song=song, loops=loops)

    def play_sound(self, sound, blocking=False):
        print('{}'.format(sound.name), end=' ', flush=True)
        sounddevice.play(sound.data_array, sound.sample_rate, blocking=blocking)

    # TODO: Improve accuracy of calculatation for when to play the next beat
    # Maybe try realigning every bar - use absolute time?
    def play_loop(self, sounds, step_time_s, loops=-1):
        """Play a note for every step in the clip

        Repeat for the specified number of loops. If loop is -1 then play continuously.
        """
        steps = len(sounds)
        loop_count = 0
        for i in itertools.cycle(range(steps)):
            now = time.time()
            # play the sound
            self.play_sound(sounds[i])
            # sleep for the remainding amount of time
            elapsed = time.time() - now
            time.sleep(max(MIN_STEP_TIME, step_time_s - elapsed))
            if i == steps - 1:
                loop_count += 1
                print('')
            if loop_count == loops:
                return

    def play_sequence(self, sequence, step_time_s=0.5, loops=-1):
        bar_time_s = (SECONDS_PER_MIN / self.settings.bpm) * self.settings.beats_per_measure
        step_time_s = bar_time_s / sequence.steps
        self.play_loop(sounds=sequence.get_sounds(), step_time_s=step_time_s, loops=loops)

    def play_clip(self, clip, loops=-1):
        self.play_sequence(sequence=clip.mix, loops=loops)

    def play_song(self, song, loops=-1):
        for clip in song.clips:
            self.play_clip(clip=clip, loops=loops)
