"""Helper-functions for Address."""
from time import time


class Timer(object):
    """Custom timer-object, to output progress to console"""

    def __init__(self, starting_progress=0, output_interval=0.5, keys=None):
        """Description."""
        self.start_time = time()
        self.last_time = self.start_time
        self.keys = keys or {}
        self.output_interval = output_interval
        self.last_output_time = output_interval
        self.starting_progress = starting_progress
        self.last_lines_cycled_real = starting_progress
        self.output_string = '{:0.0f} seconds passed'
        self.output_format = lambda timer: (
            timer.now - timer.start_time,)
        self.total_time_spent = 0
        self.now = self.start_time
        self.progress = 0
        self.lines_cycled_real = 0

    def update(self, progress):
        """Description."""
        self.now = time()
        self.progress = progress
        if self.now - self.start_time >= self.last_output_time:
            self.total_time_spent = self.now - self.start_time
            self.lines_cycled_real = self.starting_progress + self.progress
            try:
                print(self.output_string.format(*self.output_format(self)))
            except KeyError as e:
                print('Error with outputting to console. missing key: {}'
                      .format(e))
            self.last_lines_cycled_real = self.lines_cycled_real
            self.last_time = self.now
            self.last_output_time += self.output_interval
