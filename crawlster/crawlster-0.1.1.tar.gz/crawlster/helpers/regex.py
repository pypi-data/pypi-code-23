import re

from crawlster.helpers.base import BaseHelper


class RegexHelper(BaseHelper):
    """Helper that provides shortcuts for various operations with regexes

    Provides regex compiling cache for optimizing regex reusability.

    Note:
        It is strongly unrecommended to use regex to parse HTML content.
        Please see the ``.extract`` helper to more convenient and less error
        prone methods to parse HTML.
    """
    name = 'regex'

    def __init__(self):
        super(RegexHelper, self).__init__()
        self._cache = {}

    def compile(self, pattern, flags=0):
        """Compiles a regex pattern by using the cache"""
        key = self.make_cache_key(pattern, flags)
        if key in self._cache:
            compiled = self._cache.get(key)
        else:
            compiled = re.compile(pattern, flags)
            self._cache[key] = compiled
        return compiled

    @staticmethod
    def make_cache_key(pattern, flags):
        """Creates a unique cache key for every pattern"""
        return '{}_{}'.format(pattern, flags)

    def search(self, pattern, text, flags=0):
        return self.compile(pattern, flags).search(text)

    def findall(self, pattern, text, flags=0):
        return self.compile(pattern, flags).findall(text)

    def match(self, pattern, text, flags=0):
        return self.compile(pattern, flags).match(text)
