#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class IndexedFile(object):
    """
    Generic class for pre-indexed file objects.

    :param filename: file name
    :type filename: str
    :return: indexed file object
    :rtype: .IndexedFile
    """

    def __init__(self, filename):
        self.filename = filename
        self._fileByteSize = os.stat(self.filename).st_size
        self._line_offset = []
        self._currentLineIndex = 0
        self._indexFile()


    def _indexFile(self):
        """
        Generates the byte offset table.
        Method is called in :meth:`__init__`.
        """
        with open(self.filename, 'r') as f:
            offset = 0
            no = 0
            for line in f:
                self._parseLine(line, no)
                self._line_offset.append(offset)
                offset += len(line)
                no += 1


    def _parseLine(self, line, no):
        """
        Method which will be called in :meth:`._indexFile` for each line of the the File.

        :param line: line to parse
        :type line: str
        :param no: number of the line
        :type no: int
        """
        pass


    def _getOffsets(self, startLineIndex, endLineIndex):
        """

        :param startLineIndex: index of first line
        :type startLineIndex: int
        :param endLineIndex: index of last line (included!)
        :type endLineIndex: int
        :return: start byte offset and byte length
        :rtype: tuple(int, int)
        """
        # print 'startLineIndex:', startLineIndex
        # print 'len(self._line_offset):',len(self._line_offset)
        startOffset = self._line_offset[startLineIndex]
        if endLineIndex >= len(self._line_offset):
            raise IndexError,'invalid line index'
        elif endLineIndex == len(self._line_offset) - 1:
            length = self._fileByteSize - startOffset
        else:
            length = self._line_offset[endLineIndex + 1] - startOffset - 1
        return startOffset, length


    def getLines(self, startLineIndex, endLineIndex):
        """
        Returns a part of the file as a string.

        :param startLineIndex: index of first line
        :type startLineIndex: int
        :param endLineIndex: index of last line (included!)
        :type endLineIndex: int
        :return: part of the file
        :rtype: str
        """
        startOffset, length = self._getOffsets(startLineIndex, endLineIndex)
        with open(self.filename, 'r') as f:
            f.seek(startOffset)
            return f.read(length)


    def getLine(self, lineIndex):
        """
        Returns the line with a given index (0,1,..) as a string.

        :param lineIndex: index of line in file
        :type lineIndex: int
        :return: line
        :rtype: str
        """
        return self.getLines(lineIndex, lineIndex)


    def __len__(self):
        """ Returns the total number of lines in the file. (support for ``len()``"""
        return len(self._line_offset)


    def __getitem__(self, index):
        return self.getLine(index)


    def __iter__(self):
        return self


    def next(self):
        """ Returns the *next* line from the file. """
        if self._currentLineIndex < len(self._line_offset):
            line = self.getLine(self._currentLineIndex)
            self._currentLineIndex += 1
            return line
        self._currentLineIndex = 0
        raise StopIteration()


    @property
    def fileLineSize(self):
        return len(self._line_offset)
