""" Geographical coverage utility
"""
import logging
from zope.interface import implements
from eea.alchemy.interfaces import IDiscoverGeographicalCoverage
logger = logging.getLogger('eea.alchemy')

ENTITY_TYPES = [
    'City',
    'Continent',
    'Country',
    'GeographicFeature',
    'Region',
    'StateOrCounty',
]

class DiscoverGeographicalCoverage(object):
    """ Discover geotags
    """
    implements(IDiscoverGeographicalCoverage)

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
        """ Not Implemented. Alchemy API support dropped.
        """
        return None

    def __call__(self, key, text="", path=""):
        self._key = key

        if not self.alchemy:
            return

        # For future replacement of Alchemy API
        for entity in []:
            etype = entity.get('type', '')
            if etype not in ENTITY_TYPES:
                continue
            yield entity
