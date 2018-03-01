#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .indexedfile import IndexedFile


class Block(object):
    """
    Generic class for a block within an indexed block file.

    :param blockFile: block file object
    :type blockFile: pylam.base.BlockFile
    :param fline: first line index of the data block
    :type fline: int
    :param lline: last line index of the data block
    :type lline: int
    :param header_line: header of the block
    :type header_line: str
    """


    def __init__(self, blockFile, fline=0, lline=0, header_line='N/A'):
        self.blockFile = blockFile
        self.startLineIndex = int(fline)
        self.endLineIndex = int(lline)
        self.header_line = str(header_line)
        self._currentBlockLine = 0


    def __getitem__(self, index):
        """
        Support for *read only* itemized access (:attr:`self[index]`)
        to the *lines* of the block.

        :param index: block line index
        :type index: int
        :return: data
        :rtype: str
        """
        if self.startLineIndex + index > self.endLineIndex:
            raise IndexError()
        line = self.blockFile.getLine(self.startLineIndex + index)
        return line


    def __iter__(self):
        return self


    def __len__(self):
        """Returns the number of lines of the block."""
        return self.endLineIndex - self.startLineIndex + 1


    def next(self):
        """ Returns the *next* line from the block as a string. """
        if self.startLineIndex + self._currentBlockLine <= self.endLineIndex:
            line = self.blockFile.getLine(self.startLineIndex + self._currentBlockLine)
            self._currentBlockLine += 1
            return line
        self._currentBlockLine = 0
        raise StopIteration()


    def getLines(self, startLineIndex, endLineIndex):
        """
        Returns a part of the block as a string.

        :param startLineIndex: index of first line
        :type startLineIndex: int
        :param endLineIndex: index of last line (included!)
        :type endLineIndex: int
        :return: multiple lines
        :rtype: str
        """
        data_string = self.blockFile.getLines(startLineIndex + self.startLineIndex, endLineIndex + self.startLineIndex)
        return data_string


    def getLine(self, lineIndex):
        """
        Returns a line of the  block as a string.

        :param lineIndex: index of data row
        :type lineIndex: int
        :return: line
        :rtype: str
        """
        return self.getLines(lineIndex, lineIndex)


    def writeOTF(self, filename):
        """
        Writes the whole block *as it is* and *on the fly* to a separate file.
        Hence, not all the data needs to be stored in memory in between!

        :param filename: output file name
        :type filename: str
        """
        with open (filename, 'w') as f:
            if self.header_line != 'N/A':
                f.write('# '+self.header_line+'\n')
            for i in range(0, len(self)):
                f.write( self.blockFile.getLine(self.startLineIndex + i) + '\n' )


    def info(self):
        """
        Prints debug info to screen, e.g.::

            header    : This is a header line.
            size      : 100
            first line: 5
            last line : 104

        """
        print 'header    :', self.header_line
        print 'N lines   :', len(self)
        print 'first line:', self.blockFile.getLine(self.startLineIndex)
        print 'last line :', self.blockFile.getLine(self.endLineIndex)


    @property
    def data(self):
        """The *whole* block as a string."""
        data_string = self.blockFile.getLines(self.startLineIndex, self.endLineIndex)
        return data_string



class BlockFile(IndexedFile):
    """
    Bases: :class:`pylam.base.IndexedFile`

    Generic class for files containing different blocks.

    :param filename: file name
    :type filename: str
    :return: block file object
    :rtype: .BlockFile
    """

    #: Class of the *Block object* which is attached by :meth:`.addBlock`.
    blockClass = Block


    def __init__(self, filename):
        self._blocks = []
        self._currentBlock = 0
        super(BlockFile, self).__init__(filename)


    def __len__(self):
        """
        Returns the number of blocks,
        """
        return len(self._blocks)


    def __getitem__(self, index):
        """
        Support for *read only* itemized access (:attr:`self[index]`) to the *Blocks*.

        :param index: block index within the file
        :return: block object
        :rtype: .Block
        """
        return self._blocks[index]


    def __iter__(self):
        return self._blocks.__iter__()


    def getBlock(self, index):
        """
        Returns the *Block* object.

        .. deprecated:: 0.1.dev1 Use itemized access  instead!

        :param index: block index within the file
        :param index: int
        :return: block object
        :rtype: Block
        """
        return self._blocks[index]


    def addBlock(self, fline=0, lline=0, header_line='N/A'):
        """
        Adds a *Block* object of type :attr:`blockClass` to the BlockFile.

        :param fline: index of the first line of the block within the BlockFile
        :type fline: int
        :param lline: index of the last line of the block within the BlockFile
        :type lline: int
        :param header_line: an optional header
        :type header_line: str
        """
        self._blocks.append(
            self.__class__.blockClass(self, fline=fline, lline=lline, header_line=header_line)
        )
