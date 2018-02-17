# -*- coding: utf-8 -*-
"""Dictionary module.

contains PSDict
"""

from copy import copy

from puzzlestream.backend.reference import PSCacheReference


class PSDict(dict):

    """Dictionary with some extra functionality.

    Python dictionary complemented by logging changes to the dict and getting
    and deleting items from stream; basically a view on the stream.
    """

    def __init__(self, sectionID, stream, changelog=[], data={}):
        """Dictionary initialisation.

        Args:
            sectionID (int): ID of the stream section the dict belongs to.
            stream (PSStream): Puzzle Stream stream object.
            changelog (list): Initial change log.
            data (dict): Initial data.
        """
        self.__changelog = changelog
        self.__id, self.__stream = sectionID, stream

        super().__init__(data)

    def __iter__(self):
        """Iterate first over values in dict (RAM), then over stream.

        Yields:
            key (str): Key in dictionary / stream.
        """
        for key in super().__iter__():
            yield key

        for key in self.__stream:
            ID = key.split("-")[0]

            if int(ID) == self.__id:
                keyn = key.replace(ID + "-", "")

                if keyn not in self:
                    yield keyn

    def __streamKey(self, key):
        """Return stream key corresponding to key, e.g. x -> 1-x"""
        return str(self.__id) + "-" + key

    def __getitem__(self, key):
        """Get item `key` from this dict / the stream.

        Return item from RAM if possible, if not the item is loaded from the
        stream and stored in RAM for faster access later on.

        Args:
            key (str): Key of the item that is returned.

        Returns:
            data (:obj:): Object corresponding to `key`.
        """
        if super().__contains__(key):
            data = super().__getitem__(key)
        else:
            data = self.__stream.getItem(self.__id, key)
            while isinstance(data, PSCacheReference):
                data = self.__stream.getItem(int(data), key)
            super().__setitem__(key, data)
        return data

    def __setitem__(self, key, value):
        """Store item and log key in changelog.

        Args:
            key (str): Key in dict / stream.
            value (:obj:): Object to be saved.
        """
        if key not in self.changelog:
            self.changelog.append(key)
        super().__setitem__(key, value)

    def deleteFromStream(self, key):
        """Delete item `key` from stream (and this dict)."""
        if super().__contains__(key):
            super().__delitem__(key)
        del self.__stream[self.__streamKey(key)]

    def copy(self):
        """Return a copy of the dictionary."""
        return copy(self)

    def reload(self):
        """Reload cached data from stream."""
        for key in super().keys():
            super().__setitem__(key, self.__stream[self.__streamKey(key)])

    @property
    def changelog(self):
        """list, contains keys changed since last reset."""
        return self.__changelog

    def resetChangelog(self):
        """Reset changelog to an empty list."""
        self.__changelog = []

    def cleanRam(self):
        """Delete everything from Ram."""
        super().clear()
