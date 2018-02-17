# -*- coding: utf-8 -*-
"""Cache reference module.

contains PSCacheReference
"""


class PSCacheReference:

    """Cache reference to other stream sections.

    Cache references are used to avoid duplicate entries in the cache. It is
    simply a reference to another section ID.
    """

    def __init__(self, sectionID):
        """Reference init

        Args:
            sectionID (int): ID of the stream section the reference points to.
        """
        self.__sectionID = sectionID

    def __int__(self):
        return self.__sectionID

    def __str__(self):
        return "reference to " + str(self.__sectionID)

    def __repr__(self):
        return "reference to " + str(self.__sectionID)

    @property
    def sectionID(self):
        """ID of the stream section the reference points to."""
        return self.__sectionID
