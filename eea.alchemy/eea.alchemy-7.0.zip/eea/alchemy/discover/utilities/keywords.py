""" Utility for keywords
"""
import logging
from zope.interface import implements
from eea.alchemy.interfaces import IDiscoverKeywords
logger = logging.getLogger('eea.alchemy')

class DiscoverKeywords(object):
    """ Auto discover keywords
    """
    implements(IDiscoverKeywords)

    def __init__(self):
        self._key = ''
        self._alchemy = None

    @property
    def key(self):
        """ Alchemy key
        """
        return self._key

    @property
    def alchemy(self):
        """ Not Implemented. Alchemy API support dropped
        """
        return None

    def __call__(self, key, text="", path=""):
        self._key = key
        if not self.alchemy:
            return

        # For future replacement of Alchemy API
        for keyword in []:
            yield keyword
