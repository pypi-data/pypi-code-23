import threading
import copy

from crawlster.helpers.base import BaseHelper


class StatsHelper(BaseHelper):
    """Helper that tracks different statistics through the crawler"""

    def __init__(self):
        super(StatsHelper, self).__init__()
        self._stats = {}
        self._lock = threading.Lock()

    def initialize(self):
        pass

    def set(self, key, value):
        """Sets the specific stat to a fixed value"""
        with self._lock:
            self._stats[key] = value

    def get(self, key):
        """Returns the specified stat"""
        with self._lock:
            return copy.deepcopy(self._stats[key])

    def add(self, key, item):
        """Adds an item to the specified stat collection"""
        with self._lock:
            self._stats.setdefault(key, [])
            self._stats[key].append(item)

    def incr(self, key, by=1):
        """Increases the stat value by the specified amount"""
        with self._lock:
            self._stats.setdefault(key, 0)
            self._stats[key] += by

    def decr(self, key):
        """Decreases the stat value by the specified amount"""
        self.incr(key, by=-1)

    def dump(self):
        """Dumps all the stats as a dict where key is the stat name"""
        with self._lock:
            copy_dict = copy.deepcopy(self._stats)
        return copy_dict
