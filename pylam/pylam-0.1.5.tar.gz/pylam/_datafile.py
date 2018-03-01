#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from io import StringIO
import re

from .base import (IndexedFile, BlockFile, Table)
from ._block import (ThermoBlock, FixBlock)


class SimpleDataFile(IndexedFile):
    """
    Bases: :class:`pylam.base.IndexedFile`

    Class for a simple (csv) data file with an optional header line.

    :param filename: file name
    :type filename: str
    :param header_prefix: prefix of header line (default: ``#``)
    :type header_prefix: str
    :param delimiter: string used to separate values (default: any whitespace)
    :type delimiter: str
    :return: simple data file object
    :rtype: .SimpleDataFile

    """

    def __init__(self, filename, header_prefix='#', delimiter=None):
        self.header_line = None
        self._header = None
        self._header_prefix = header_prefix
        self._delimiter = delimiter
        self._number_of_headerlines = 0
        self._currentRowIndex = 0
        super(SimpleDataFile, self).__init__(filename)
        self._get_header()


    def _get_header(self):
        header_line = super(SimpleDataFile, self).getLines(0, 0)
        #print 'h:', header_line
        if self._header_prefix in header_line:
            self._header = str(header_line.strip()[2:]).split()
            self.header_line = header_line
            self._number_of_headerlines = 1
            self._currentLineIndex = 1


    def _dataStr2npArray(self, data_string):
        data_string = StringIO(unicode(data_string))
        return np.loadtxt(data_string, delimiter=self._delimiter)


    def getRows(self, startRowIndex, endRowIndex):
        """
        Returns a part of the file as a numpy array.

        :param startRowIndex: index of first data row
        :type startRowIndex: int
        :param endRowIndex: index of last data row (included!)
        :type endRowIndex: int
        :return: data
        :rtype: numpy.ndarray
        """
        startRowIndex += self._number_of_headerlines
        endRowIndex += self._number_of_headerlines
        data_string = self.getLines(startRowIndex, endRowIndex)
        return self._dataStr2npArray(data_string)


    def getRow(self, rowIndex):
        """
        Returns the data in row with index (0,1,..) as a numpy array.

        :param rowIndex: index of data row in file
        :type rowIndex: int
        :return: data
        :rtype: numpy.ndarray
        """
        return self.getRows(rowIndex, rowIndex)


    def getCol(self, idx):
        """
        Returns a *whole* column as a np.ndarray.

        :param idx: column index
        :type idx: int
        :return: column data
        :rtype: np.ndarray
        """
        return self.data[:, idx]


    @property
    def data(self):
        """
        :return: the *whole* data
        :rtype: numpy.ndarray
        """
        data_string = self.getLines(self._number_of_headerlines, self.fileLineSize-1)
        return self._dataStr2npArray(data_string)


    @property
    def header(self):
        """
        :return: the header line as list
        :rtype: list
        """
        return self._header


    @property
    def properHeader(self):
        """
        :return: tests if a proper *header* is defined
        :rtype: bool
        """
        self.ncolumns = len(self.getRow(0))
        if len(self._header) == self.ncolumns:
            return True
        else:
            return False


    def info(self):
        """
        Prints debug info to screen, e.g.::

            file name        : example_data_files/simple.dat
            data header      : ['Chunk', 'Coord1', 'Ncount', 'v_temp']
            number of lines  : 491

        """
        print 'file name        :', self.filename
        print 'data header      :', self.header
        print 'number of lines  :', self.fileLineSize



    def columnName2Index(self, name):
        """
        Returns the column *index* for a given *name* as defined in the header.
        Therefore :attr:`pylam.SimpleDataFile.properHeader` must be *True*.

        :param name: column name
        :type name: str
        :return: column index
        :rtype: int
        """
        if not self.properHeader:
            raise StandardError('No proper header defined. You can not use names to access columns.')
        if name not in self.header:
            msg = "Column name '" + name + "' not defined."
            raise NameError(msg)
        return self.header.index(name)


    def getColumnByName(self, name):
        # type: (object) -> object
        """
        Returns a *whole* column as a np.ndarray.

        :param name: column name
        :type name: str
        :return: column data
        :rtype: np.ndarray
        """
        idx = self.columnName2Index(name)
        return self.data[:, idx]


    def __getitem__(self, index):
        return self.getRow(index)


    def __len__(self):
        """ Returns the number of *data* rows. (support for ``len()``)"""
        return self.fileLineSize - self._number_of_headerlines


    def next(self):
        """ Returns the data of the *next* row from the file as numpy array."""
        if self._currentRowIndex < self.fileLineSize + self._number_of_headerlines - 1:
            line = self.getRow(self._currentRowIndex)
            self._currentRowIndex += 1
            return line
        self._currentRowIndex = 0
        raise StopIteration()


#=======================================================================================================================


class FixBlockFile(BlockFile):
    """
    Bases: :class:`pylam.base.BlockFile`

    Class for LAMMPS fix data files.

    :param filename: file name
    :type filename: str
    :return: fix block data file object
    :rtype: .FixBlockFile
    """

    #: Block class which is attached, here: :class:`pylam.DataBlock`
    blockClass = FixBlock


    def __init__(self, filename):
        self._blockHeaderLines = 1
        super(FixBlockFile, self).__init__(filename)
        self._anaHeader()
        self._readHeader()
        self._createBlocks()

    def _anaHeader(self):
        self._fileHeaderLines = 0
        while '# ' == str(self.getLine(self._fileHeaderLines))[0:2]:
            self._fileHeaderLines += 1

        if self._fileHeaderLines == 2:
            self._multi = False
            self._blockHeaderLines = 0
        elif self._fileHeaderLines == 3:
            self._multi = True
            self._blockHeaderLines = 1
        else:
            raise StandardError('Not a valid file format.')

    def _readHeader(self):
        self.title = str(self.getLine(0).strip())[2:]
        self.data_type = self.title.split()[0]
        if self._multi:
            self.block_header = str(self.getLine(1).strip())[2:].split()
            self.data_header_line = self.getLine(2)[2:]
            self.data_header = str(self.data_header_line.strip()).split()
            self.blocksize = int(self.getLine(3).strip().split()[1])
        else:
            self.block_header = None
            self.data_header_line = self.getLine(1)[2:]
            self.data_header = str(self.data_header_line.strip()).split()
            self.blocksize = self.fileLineSize - self._fileHeaderLines

    def _createBlocks(self):
        nblocks = (self.fileLineSize - self._fileHeaderLines) / \
                  (self.blocksize  + self._blockHeaderLines)
        for i in range(0, nblocks):
            startLineIndex = self._fileHeaderLines + self._blockHeaderLines
            startLineIndex += (self.blocksize + self._blockHeaderLines) * i
            endLineIndex = startLineIndex + self.blocksize - 1
            # print startLineIndex, endLineIndex
            self.addBlock(fline=startLineIndex, lline=endLineIndex, header_line=self.data_header_line)
            if self.block_header:
                bhd = self.getLine(startLineIndex-1).strip().split()
                temp = {}
                for i in range(0, len(self.block_header)):
                    temp[self.block_header[i]] = bhd[i]
                self._blocks[-1].blockHeaderData = temp

    def aveBlocks(self,bids):
        """
        Average over blocks.

        :param bids: list of block ids to use for average
        :type bids: list
        :return: numpy array containing the 'average block'
        :rtype: numpy.ndarray
        """
        _data_sets = []
        for bid in bids:
            if bid not in range(0, len(self)):
                raise IndexError('Invalid block ID!')
            _data_sets.append(self[bid])
        num_rows = len(_data_sets[0])
        num_cols = len(_data_sets[0][0])
        data_new = np.zeros((num_rows,num_cols))
        for i in range(0, num_rows):
            for j in range(0, num_cols):
                for k in range(0, len(_data_sets)):
                    data_new[i][j] += _data_sets[k][i][j]
                data_new[i][j] = data_new[i][j]/len(_data_sets)
        return data_new

    def info(self):
        """
        Prints debug info to screen, e.g.::

            file name        : example_data_files/chunk1D.dat
            title            : Chunk-averaged data for fix TPROFILE and group all
            data type        : Chunk-averaged
            block header     : ['Timestep', 'Number-of-chunks', 'Total-count']
            data header      : ['Chunk', 'Coord1', 'Ncount', 'v_temp']
            block size       : 121
            number of lines  : 491
            number of blocks : 4
            multi            : True

        """
        print 'file name        :', self.filename
        print 'title            :', self.title
        print 'data type        :', self.data_type
        print 'block header     :', self.block_header
        print 'data header      :', self.data_header
        print 'block size       :', self.blocksize
        print 'number of lines  :', self.fileLineSize
        print 'number of blocks :', len(self)
        print 'multi            :', self._multi

    def columnName2Index(self, name):
        """
        The index of the column with a given name.

        :param name: name of the column (property)
        :type name: str
        :return: index of the column
        :rtype: int
        """
        if name not in self.data_header:
            msg = "Column name '" + name + "' not defined."
            raise NameError(msg)
        return self.data_header.index(name)

    def blocks2cols(self, colname, fix=[]):
        """
        Extracts a selected column (property) from a each block and combines them.

        For example, if ``chunk1D.dat`` looks like::

            # Chunk-averaged data for fix TPROFILE and group all
            # Timestep Number-of-chunks Total-count
            # Chunk Coord1 Ncount v_temp
            500000 121 2000
            1 0.0881802 12.1949 0.842912
            2 0.264541 12.09 0.842986
            3 0.440901 12.0788 0.840996
            ...
            1000000 121 2000
            1 0.0881802 11.6526 0.841493
            2 0.264541 11.7525 0.840792
            3 0.440901 11.7087 0.842102
            ...
            ...

        with

        >>> import pylam
        >>> FBF = pylam.FixBlockFile('chunk1D.dat')
        >>> newTable = FBF.blocks2cols('v_temp', fix=['Chunk','Coord1'])
        >>> newTable.write('new.dat')

        ``new.dat`` will look like::

            # Chunk Coord1 v_temp_0 v_temp_1 v_temp_2 v_temp_3
            +1.00000000e+00 +8.81802000e-02 +8.42912000e-01 +8.41493000e-01 +8.40999000e-01 +8.43067000e-01
            +2.00000000e+00 +2.64541000e-01 +8.42986000e-01 +8.40792000e-01 +8.45285000e-01 +8.40694000e-01
            +3.00000000e+00 +4.40901000e-01 +8.40996000e-01 +8.42102000e-01 +8.40272000e-01 +8.44249000e-01
            +4.00000000e+00 +6.17262000e-01 +8.37955000e-01 +8.37166000e-01 +8.39804000e-01 +8.38266000e-01

        :param colname: selected column to collect
        :param fix: common column (like, e.g. 'Bin')
        :return: Table object
        :rtype: pylam.base.Table
        """
        ncols = len(fix) + len(self)
        data = np.zeros((len(self[0]), ncols))
        n = 0
        for f in fix:
            fid = self.columnName2Index(f)
            data[:,n] = self[0].getColumnByName(f)
            n += 1
        props = fix
        for i in range(0, len(self)):
            temp=str('{0:s}_{1:d}'.format(colname, i))
            props.append( temp )
            data[:,n] = self[i].getColumnByName(colname)
            n += 1
        return Table(data_in=data, props=props)


#=======================================================================================================================


class LogFile(BlockFile):
    """
    Bases: :class:`pylam.base.BlockFile`

    Class for LAMMPS log files.

    :param filename: log file name
    :type filename: str
    :return: log file object
    :rtype: .LogFile
    """

    _start_pattern = ('Memory usage ', 'Per MPI rank memory allocation ')
    _end_pattern = ('Loop time',)

    #: Block class which is attached, here: :class:`pylam.ThermoBlock`
    blockClass = ThermoBlock


    def __init__(self, filename):
        self.totalSteps = 0
        self.totalTime = 0.0
        self.natoms = None
        self.groups = {}

        self._start_regex = re.compile('|'.join(self._start_pattern))
        self._end_regex = re.compile('|'.join(self._end_pattern))

        self.__in_block = False
        self.__temp_fline = None
        self.__temp_hline = None
        self.runs = []
        self._parse_dict={'orthogonal box': self._parseBox,
                          'units': self._parseUnits,
                          'atoms in group': self._parseGroup}
        super(LogFile, self).__init__(filename)
        self._postParse()

    def _is_block_start(self, line):
        # for kw in self._start_pattern:
        #    if kw in line:
        #        return True
        # return False
        # or
        # return any(kw in line for kw in self._start_pattern)
        # or
        return re.search(self._start_regex, line) is not None

    def _is_block_end(self, line):
        # for kw in self._end_pattern:
        #    if kw in line:
        #        return True
        # return False
        # or
        # return any(kw in line for kw in self._end_pattern)
        # or
        return re.search(self._end_regex, line) is not None


    def _parseLine(self, lineString, lineIndex):
        if self.__in_block:                                      # ---- we are IN a thermo block ----
            if not self.__temp_hline:                           # if header not already set, set it...
                self.__temp_hline = lineString.strip()
            #elif self.__class__._end_pattern in lineString:     # find 'end' pattern
            elif self._is_block_end(lineString):
                self.addBlock(fline=self.__temp_fline, lline=lineIndex - 1, header_line=self.__temp_hline)
                self.__in_block = False
        else:                                                   # ---- we are NOT IN a thermo block ----
            #if self.__class__._start_pattern in lineString:     # find 'start' pattern
            if self._is_block_start(lineString):
                self.__in_block = True
                self.__temp_fline = lineIndex+2
                self.__temp_hline = None
            elif '#' != lineString[0]:
                self._parseKeyWords(lineString)                 # keyword scan


    def _postParse(self):
        natoms = []
        for tblock in self:
            self.totalTime += tblock.runprops['rtime']
            self.totalSteps += tblock.runprops['steps']
            natoms.append(tblock.runprops['atoms'])
        if len(set(natoms)) == 1:
            self.natoms = natoms[0]
        else:
            self.natoms = natoms


    def _parseKeyWords(self, lineString):
        for key in self._parse_dict.keys():
            if key in lineString:
                self._parse_dict[key](lineString)


    def _parseBox(self, line):
        h0 = line.strip().split()[-7:-4]
        h1 = line.strip().split()[-3:]
        self.box = {'xlo': float(h0[0][1:]), 'ylo': float(h0[1]), 'zlo': float(h0[2][:-1]),
                    'xhi': float(h1[0][1:]), 'yhi': float(h1[1]), 'zhi': float(h1[2][:-1])}
        self.box['Lx'] = self.box['xhi'] - self.box['xlo']
        self.box['Ly'] = self.box['yhi'] - self.box['ylo']
        self.box['Lz'] = self.box['zhi'] - self.box['zlo']
        self.box['V'] =  self.box['Lx'] * self.box['Ly'] * self.box['Lz']
        self.box['Axy'] = self.box['Lx'] * self.box['Ly']
        self.box['Axz'] = self.box['Lx'] * self.box['Lz']
        self.box['Ayz'] = self.box['Ly'] * self.box['Lz']


    def _parseUnits(self, line):
        if len(line.strip().split()) == 2:
            self.units = line.strip().split()[1]
            #print '-> units:', self.units

    def _parseGroup(self, line):
        w = line.strip().split()
        if len(w) == 5:
            self.groups[w[4]] = int(w[0])

    def info(self, re=False):
        """
        Prints debug info to screen, e.g.::

            file name:        example_data_files/log.lammps
            units:            real
            N atoms           1372
            N runs:           3
            total run time:   3682.2074 sec
            total steps:      5010000

        :param re: recursive info for :class:`pylam.ThermoBlock`
        :type re: bool
        """
        print 'file name:       ', self.filename
        print 'units:           ', self.units
        print 'N atoms          ', self.natoms
        print 'N runs:          ', len(self)
        print 'total run time:  ', self.totalTime,'sec'
        print 'total steps:     ', self.totalSteps
        if re:
            print 'run info:'
            for i in range(0, len(self)):
                print '-'*10 + 'run ' + str(i) + ' ' + '-'*10
                self.__getitem__(i).info()
