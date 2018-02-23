""" Alchemy adapters
"""
import logging
from zope.interface import implements
from eea.alchemy.interfaces import IDiscoverAdapter
from eea.alchemy.config import EEAMessageFactory as _
logger = logging.getLogger('eea.alchemy')

class Discover(object):
    """ Abstract alchemy adapter.

        All custom alchemy adapters should inherit from this  adapter or at
        least implement it's methods and attributes. See IDiscoverAdapter
        interface for more details.

    """
    implements(IDiscoverAdapter)
    title = _('Abstract')

    def __init__(self, context):
        self.context = context
        self._key = None
        self.field = 'subject'
        self._metadata = ('title', 'description')

    @property
    def metadata(self):
        """ Get metadata
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        """ Set metadata
        """
        if isinstance(value, (str, unicode)):
            value = (value,)
        self._metadata = value
