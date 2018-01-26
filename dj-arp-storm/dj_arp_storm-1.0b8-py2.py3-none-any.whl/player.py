import threading
from collections import OrderedDict
from glob import glob
from os import listdir, path
import os
import sys
from time import sleep
import pygame


# Define a context manager to suppress stdout and stderr.
class suppress_stdout_stderr(object):
    '''
    stolen from: https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])

class Player(object):
    def __init__(self, instrument_path, channel_count=60):
        """Init the instance.

        :param instrument_path: Path to the top level folder holding sound files.
        :type instrument_path: string
        :param channel_count: Number of channels to start the mixer with.
        :type channel_count: int
        """
        self.instrument_path = instrument_path
        self.sounds = OrderedDict()
        self.channel_count = channel_count
        with suppress_stdout_stderr():
            pygame.mixer.quit()
            pygame.mixer.init(frequency=44100,size=-16,channels=2,buffer=65536)
            pygame.mixer.quit()
            pygame.mixer.init(44100, -16, 2, 4096)
            pygame.mixer.set_num_channels(channel_count)

    def load(self):
        """Load all the sound files from the specified asset dir as pygame.mixer.Sound objects."""
        for instrument in listdir(self.instrument_path):
            instrument_full = path.join(self.instrument_path, instrument)
            notes = glob(path.join(instrument_full, "*.ogg"))
            paths = [path.abspath(path.join(instrument_full, note)) for note in notes]
            self.sounds[instrument] = OrderedDict(
                (path.basename(note), pygame.mixer.Sound(path.abspath(note))) for note in notes
            )

    @staticmethod
    def play(note):
        """Play a sound.

        Find an open channel on the mixer and queue the sound on it.

        :param note: The sound object to play.
        :type note: pygame.mixer.Sound
        """
        # TODO rather than find_channel just use a round robin
        # the sounds are getting queued, so waiting on a channel to be open
        # could cause a larger delay than jsut queuing behind the first
        # channel again.
        channel = None
        while channel is None:
            channel = pygame.mixer.find_channel()
        channel.queue(note)

    def delay_play(self, note, delay=1):
        """Play a sound after a specified delay.

        Fire a thread timer to trigger a sound object after a delay.

        :param note: The sound object to play.
        :type note: pygame.mixer.Sound
        :param delay: The delay in seconds to play the note.
        :type delay: int
        """
        threading.Timer(delay, Player.play, [note]).start()

    def scale(self, instrument, mod=1):
        """Play all the notes of an instrument.

        :param instrument: The name of the folder holding the notes to play.
        :type instrument: string
        :param mod: The delay between notes when playing the scale.
        :type mod: int,float
        """
        for delay, note  in enumerate(instrument.values()):
            self.delay_play(note, (1+delay)*mod)

if __name__ == "__main__":
    player = Player(sys.argv[1])
    player.load()
    player.scale(player.sounds['piano'], mod=0.5)
    player.scale(player.sounds['guitar'], mod=0.3)
    sleep(10)
