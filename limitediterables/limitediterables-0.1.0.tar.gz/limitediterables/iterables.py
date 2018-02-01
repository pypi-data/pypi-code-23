import collections.abc
import time


class LimitedIterable(collections.abc.Iterator):

    def __init__(self, target, limit=None):
        self.target = iter(target)
        self._last_call = 0
        # TODO: Make this less horrible.
        if limit:
            self.limit = abs(limit)
            self._pause_time = 1 / self.limit  # time between each iteration.
        else:
            self.limit = None
            self._pause_time = 0

    def __iter__(self):
        return self

    def __next__(self):
        time_now = time.perf_counter()

        next_iter = self._last_call + self._pause_time
        if time_now > next_iter:
            # Update last call time.
            self._last_call = time_now
            return next(self.target)
        else:
            # Sleep until next iter time.
            time.sleep(next_iter - time_now)
            self._last_call = time.perf_counter()
            return next(self.target)
