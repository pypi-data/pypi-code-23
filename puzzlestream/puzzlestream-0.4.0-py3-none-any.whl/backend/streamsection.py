# -*- coding: utf-8 -*-
"""Stream section module.

contains PSStreamSection
"""


from puzzlestream.backend.dict import PSDict
from puzzlestream.backend.reference import PSCacheReference


class PSStreamSection:
    """Stream section class - a view on the stream.

    A stream section is basically a view on one puzzle item's section of the
    stream. It holds the data itself (.data, a PSDict) as well as a record of
    all changes, the change log.
    """

    def __init__(self, sectionID, stream):
        """Stream section init.

        Args:
            sectionID (int): ID of the puzzle item this section belongs to.
            stream (PSStream): The current PuzzleStream stream instance.
        """
        self.__stream = stream
        self.__id = sectionID
        self.changelog = {}

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)

    @property
    def id(self):
        """ID of the puzzle item this section belongs to."""
        return self.__id

    def updateData(self, lastStreamSectionID, data, log, clean=False):
        """Update section data and log changes.

        Args:
            lastStreamSectionID (int): Previous section; may be referenced.
            data (PSDict): Data to be stored.
            log (list): List of items changed.
            clean (bool): Whether the stream should be cleared from outdated
                stuff after updating.
        """
        for key in data:
            if key in self.changelog and key not in log:
                ref = PSCacheReference(lastStreamSectionID)
                if key in data:
                    del data[key]
                data[key] = ref

        for key in data:
            self.__stream.setItem(self.__id, key, data[key])

        self.__logChanges(log)
        if clean:
            self.__cleanStream(self.changelog)

    def __cleanStream(self, log):
        """Clean stream from outdated elements."""
        for key in self.__stream:
            ID = key.split("-")[0]
            keyn = key.replace(ID + "-", "")

            if keyn not in log and int(ID) == self.__id:
                del self.__stream[key]

    def __logChanges(self, log):
        """Update change log."""
        for item in log:
            if item in self.changelog:
                self.changelog[item].append(self.__id)
            else:
                self.changelog[item] = [self.__id]
        self.data.resetChangelog()

    @property
    def data(self):
        """Stream section data (PSDict)."""
        return PSDict(self.__id, self.__stream)

    def addSection(self, streamSection):
        """Add data of other stream section to this one, update change log.

        Args:
            streamSection (PSStreamSection): Section to be added.
        """
        for key in streamSection.changelog:
            ref = PSCacheReference(streamSection.id)
            self.__stream.setItem(self.__id, key, ref)
        self.changelog.update(streamSection.changelog)

    def copy(self, sectionID):
        """Return a copy of this section.

        Args:
            sectionID (int): ID of the new section.
        """
        new = PSStreamSection(sectionID, self.__stream)
        new.addSection(self)
        return new
