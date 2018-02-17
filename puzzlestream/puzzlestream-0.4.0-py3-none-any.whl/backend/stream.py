# -*- coding: utf-8 -*-
"""Stream module.

contains PSStream
"""

import diskcache as dc

from puzzlestream.backend.reference import PSCacheReference


class PSStream(dc.Cache):

    """Subclass of diskcache Cache; the central background harddisk cache."""

    def __init__(self, path, *args):
        """Cache init.

        Args:
            path (str): Cache directory.
            *args: All other args, passed to dc.Cache
        """
        super().__init__(path, *args)

    def getItem(self, ID, key):
        """Get item from cache.
        
        Args:
            ID (int): Stream section ID.
            key (str): Requested key.

        Returns:
            Cached data at "ID-key".
        """
        item = super().__getitem__(str(ID) + "-" + str(key))

        # delete item if it is a reference to something that no longer exists
        if (isinstance(item, PSCacheReference) and not
                super().__contains__(str(item.sectionID) + "-" + str(key))):
            super().__delitem__(str(ID) + "-" + str(key))
            raise KeyError

        return item

    def setItem(self, ID, key, data):
        """Store data in cache.
        
        Args:
            ID (int): Stream section ID.
            key (str): Key to use.
            data: Data that should be stored; must be pickable!
        """
        super().__setitem__(str(ID) + "-" + str(key), data)
