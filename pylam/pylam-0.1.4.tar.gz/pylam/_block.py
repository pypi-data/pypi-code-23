#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
from io import StringIO

from .base import Block
from .base import dict2table


class DataBlock(Block):
    """
    Bases: :class:`pylam.base.Block`

    Generic class for a data block within an indexed block file.

    :param blockFile: block file object
    :type blockFile: pylam.base.BlockFile
    :param fline: first line index of the data block
    :type fline: int
    :param lline: last line index of the data block
    :type lline: int
    :param header_line: header of the block
    :type header_line: str
    """

    #: The string used to separate values in a data row (default: ``None`` = any whitespace).
    data_delimiter = None

    def __init__(self, blockFile, fline=0, lline=0, header_line='N/A'):
        super(DataBlock, self).__init__(blockFile, fline, lline, header_line)

    def _dataStr2npArray(self, data_string):
        data_string = StringIO(unicode(data_string))
        return np.loadtxt(data_string, delimiter=self.__class__.data_delimiter)

    def __getitem__(self, index):
        """
        Support for *read only* itemized access.

        :param index: block line index
        :return: data
        :rtype: numpy.ndarray
        """
        line = super(DataBlock, self).__getitem__(index)
        return self._dataStr2npArray(line)

    def next(self):
        """ Returns the *next* data row from the block as numpy array. """
        if self.startLineIndex + self._currentBlockLine <= self.endLineIndex:
            line = self.blockFile.getLine(self.startLineIndex + self._currentBlockLine)
            self._currentBlockLine += 1
            return self._dataStr2npArray(line)
        self._currentBlockLine = 0
        raise StopIteration()

    def getRows(self, startRowIndex, endRowIndex):
        """
        Returns a part of the data block as a numpy array.

        :param startRowIndex: index of first data row
        :type startRowIndex: int
        :param endRowIndex: index of last data line (included!)
        :type endRowIndex: int
        :return: data
        :rtype: numpy.ndarray
        """
        if startRowIndex < 0:
            startRowIndex += len(self)
        if endRowIndex < 0:
            endRowIndex += len(self)
        data_string = self.blockFile.getLines(startRowIndex + self.startLineIndex, endRowIndex + self.startLineIndex)
        return self._dataStr2npArray(data_string)

    def getRow(self, rowIndex):
        """
        Returns a row of the data block as a numpy array.

        :param rowIndex: index of data row
        :type rowIndex: int
        :return: data
        :rtype: numpy.ndarray
        """
        return self.getRows(rowIndex, rowIndex)

    def getRowAsDict(self, rowIndex):
        if not self.properHeader:
            raise StandardError('Function not available. No proper header defined.')
        data = self.getRow(rowIndex=rowIndex)
        out = {}
        for i in range(0, len(data)):
            out[self.header[i]] = data[i]
        return out

    def getCol(self, idx):
        """
        Returns a *whole* column as a np.ndarray.

        :param idx: column index
        :type idx: int
        :return: column data
        :rtype: np.ndarray
        """
        return self.data[:, idx]

    def write(self, filename):
        """
        Writes the whole data block to a file.

        :param filename: output file name
        :type filename: str
        """
        np.savetxt(filename, self.data, fmt='%+1.8e', delimiter=' ',
                   newline='\n', header=self.header_line, comments='# ')

    @property
    def data(self):
        """
        :return: the *whole* data block
        :rtype: numpy.ndarray
        """
        data_string = self.blockFile.getLines(self.startLineIndex, self.endLineIndex)
        return self._dataStr2npArray(data_string)

    @property
    def header(self):
        """
        :return: the header line as list
        :rtype: list
        """
        return str(self.header_line.strip()).split()

    def info(self):
        """
        Prints debug info to screen, e.g.::

            header      : ['Step', 'Temp', 'E_pair', 'E_mol', 'TotEng', 'Press']
            N rows      : 101
            N cols      : 6
            prop. header: True

        """
        print 'header      :', self.header
        print 'N rows      :', len(self)
        print 'N cols      :', len(self[0])
        print 'prop. header:', self.properHeader

    @property
    def properHeader(self):
        """
        :return: tests if a proper *header* is defined
        :rtype: bool
        """
        self.ncolumns = len(self.getRow(0))
        if len(self.header) == self.ncolumns:
            return True
        else:
            return False

    def columnName2Index(self, name):
        """
        Returns the column *index* for a given *name* as defined in the header.
        Therefore :meth:`.properHeader` must be *True*.

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
        """
        Returns a *whole* column as a np.ndarray.

        :param name: column name
        :type name: str
        :return: column data
        :rtype: np.ndarray
        """
        idx = self.columnName2Index(name)
        return self.data[:, idx]

    def aveColumn(self, idx=None, name=None):
        if idx:
            data = self.getCol(idx)
        elif name:
            data = self.getColumnByName(name)
        else:
            raise StandardError()
        return np.average(data)

    def stdColumn(self, name):
        data = self.getColumnByName(name)
        return np.std(data)

    def varColumn(self, name):
        data = self.getColumnByName(name)
        return np.var(data)


    def statCol(self, idx):
        data = self.getCol(idx)
        out = {}
        out['ave'] = np.average(data)
        out['std'] = np.std(data)
        out['var'] = np.var(data)
        return out


    def statColAll(self):
        if not self.properHeader:
            raise StandardError('Function not available. No proper header defined.')
        out = {}
        for i in range(0, len(self.header)):
            out[self.header[i]] = self.statCol(idx=i)
        return out

    def showStat(self):
        _stat_data = self.statColAll()
        print 'col\prop   ave                  std                  var'
        print '-'*80
        for key in _stat_data.keys():
            print '{0:{width}}'.format(key, width=10),
            print '{0:{width}}'.format(str(_stat_data[key]['ave']), width=20),
            print '{0:{width}}'.format(str(_stat_data[key]['std']), width=20),
            print '{0:{width}}'.format(str(_stat_data[key]['var']), width=20)



class ThermoBlock(DataBlock):
    """
    Bases: :class:`pylam.DataBlock`

    Class for a LAMMPS thermo block within a LAMMPS log file.

    :param logFile: LogFile object
    :type logFile: pylam.LogFile
    :param fline: first line index of the thermo block
    :type fline: int
    :param lline: last line index of the thermo block
    :type lline: int
    :param header_line: header of the block
    :type header_line: str
    """

    def __init__(self, logFile, fline=0, lline=0, header_line='N/A'):
        super(ThermoBlock, self).__init__(logFile, fline=fline, lline=lline, header_line=header_line)
        self._timing = {}     # timing statistics for simulation run
        self._runprops = {}   # properties of the simulation run
        self._benchmark = {}  # benchmark key values


    def info(self):
        """
        Prints debug info to screen, e.g.::

            header      : ['Step', 'Temp', 'E_pair', 'E_mol', 'TotEng', 'Press']
            N rows      : 101
            N cols      : 6
            prop. header: True
            runprops:
             ─────────── ───────────
               keyword      value
             ─────────── ───────────
                   rtime      20.814
                   steps       10000
                   mempp      4.1816
                  thermo         100
                   procs          16
                   atoms        1372
             ─────────── ───────────

        """
        super(ThermoBlock, self).info()
        print 'runprops    :'
        dict2table(self.runprops)
        print ''


    @property
    def thermo(self):
        """
        Returns the *thermo* value.

        .. deprecated:: 0.1.dev1 Use :attr:`.runprops['thermo']` instead!
        """
        return self.runprops['thermo']

    @property
    def steps(self):
        """
        Returns the *steps* value.

        .. deprecated:: 0.1.dev1 Use :attr:`.runprops['steps']` instead!
        """
        return self.runprops['steps']


    def get_stats(self):
        steps_per_sec = self.runprops['steps'] / self.runprops['rtime']
        print 'steps/s :',steps_per_sec
        print self.timing
        print self.runprops
        print self.benchmark


    def _calc_benchmark(self):
        self._benchmark = dict(
            steps_per_sec = self.runprops['steps'] / self.runprops['rtime'],
            steps_per_sec_proc = self.runprops['steps'] / self.runprops['rtime'] / self.runprops['procs'],
            atoms_steps_per_sec = self.runprops['atoms'] * self.runprops['steps'] / self.runprops['rtime'],
            atoms_steps_per_sec_proc = self.runprops['atoms'] * self.runprops['steps'] / self.runprops['rtime']  / self.runprops['procs']
        )

    @property
    def benchmark(self):
        """
        Dictionary containing benchmark information of the simulation run.

        =========================  ==========  ======================================
        Keyword                    Value Type  Description
        =========================  ==========  ======================================
        steps_per_sec              *float*     steps / sec.
        steps_per_sec_proc         *float*     steps / ( sec. * process )
        atoms_steps_per_sec        *float*     ( atoms * steps ) / sec.
        atoms_steps_per_sec_proc   *float*     ( atoms * steps ) / ( sec. * process )
        =========================  ==========  ======================================

        :return: simulation run benchmark
        :rtype: dict
        """
        if not self._benchmark:
            self._calc_benchmark()
        return self._benchmark

    def print_benchmark(self):
        """
        Print the simulation run benchmark to screen, e.g.::

            Benchmarks:
             ───────────────────────── ─────────────────────────
                         steps_per_sec                    480.44
                    steps_per_sec_proc                    30.027
                   atoms_steps_per_sec                6.5916e+05
              atoms_steps_per_sec_proc                     41197
             ───────────────────────── ─────────────────────────

        """
        print 'Benchmarks:'
        kworder = ['steps_per_sec', 'steps_per_sec_proc', 'atoms_steps_per_sec', 'atoms_steps_per_sec_proc']
        dict2table(self.benchmark, kworder=kworder, headers=None, width=25)
        print ''


    def _get_runprops(self):
        words = self.blockFile.getLine(self.endLineIndex + 1).strip().split()
        self._runprops = dict(
            steps  = int(words[-5]),
            rtime  = float(words[3]),
            procs  = int(words[5]),
            thermo = int(words[-5]) / (len(self) - 1),
            atoms  = int(words[-2]),
            mempp  = float( self.blockFile.getLine(self.startLineIndex - 2).strip().split()[-2] )
        )


    @property
    def runprops(self):
        """
        Dictionary containing general properties of the simulation run.

        ==========  ==========  ====================================
        Keyword     Value Type  Description
        ==========  ==========  ====================================
        steps       *int*       number of simulation steps
        rtime       *float*     simtime [sec.]
        procs       *int*       number of processes used
        atoms       *int*       number of atoms
        thermo      *int*       sample interval [steps]
        mempp       *float*     memory usage per processor [Mbytes]
        ==========  ==========  ====================================

        :return: simulation run properties
        :rtype: dict
        """

        if not self._runprops:
            self._get_runprops()
        return self._runprops


    def _get_timing(self):
        """
        Populates the dictionary :attr:`._timing` by parsing the **new** *timing breakdown* section.
        """
        self._timing = dict(
            Pair = [None, None],
            Bond = [None, None],
            Kspace = [None, None],
            Neigh = [None, None],
            Comm = [None, None],
            Output = [None, None],
            Modify = [None, None],
            Other = [None, None]
        )
        KW = self.blockFile.getLine(self.endLineIndex + 3).strip().split()[0]
        if KW == 'Performance:':
            self._get_timing_new()
        elif KW == 'Pair':
            self._get_timing_old()


    def _get_timing_new(self):
        """
        Populates the dictionary :attr:`._timing` by parsing the **new** *timing breakdown* section, at the footer of a run log.
        """
        i = 0
        words = self.blockFile.getLine(self.endLineIndex + 9 + i).strip().split()
        while words and words[0] in self._timing.keys():

            if len(words) == 11:
                self._timing[words[0]] = [float(words[4]), float(words[10])]
            elif len(words) == 8:
                self._timing[words[0]] = [float(words[3]), float(words[7])]
            i += 1
            words = self.blockFile.getLine(self.endLineIndex + 9 + i).strip().split()


    def _get_timing_old(self):
        """
        Populates the dictionary :attr:`._timing` by parsing the **old** *timing breakdown* section, at the footer of a run log.
        """
        transKW = dict(
            Outpt = 'Output',
            Kspce = 'Kspace'
        )
        i = 0
        words = self.blockFile.getLine(self.endLineIndex + 3 + i).strip().split()
        while words and words[0] in self._timing.keys():
            self._timing[words[0]] = [float(words[4]),  float(words[5][1:-1])]
            i += 1
            words = self.blockFile.getLine(self.endLineIndex + 3 + i).strip().split()
            if words and words[0] in transKW.keys():
                words[0] = transKW[words[0]]


    @property
    def timing(self):
        """
        The statistics from the *timing breakdown* below the thermodynamic block data, like::

            MPI task timing breakdown:
            Section |  min time  |  avg time  |  max time  |%varavg| %total
            ---------------------------------------------------------------
            Pair    | 144.79     | 149.62     | 153.95     |  17.4 | 13.10
            Bond    | 16.294     | 16.504     | 17.38      |   4.7 |  1.45
            Kspace  | 621.19     | 626.01     | 630.98     |   9.0 | 54.81
            Neigh   | 261.86     | 262.18     | 262.44     |   1.0 | 22.96
            Comm    | 66.306     | 71.848     | 75.624     |  30.6 |  6.29
            Output  | 0.054085   | 0.076193   | 0.089217   |   4.2 |  0.01
            Modify  | 11.62      | 15.304     | 20.772     |  65.9 |  1.34
            Other   |            | 0.5473     |            |       |  0.05

        , or the *old* format::

            Pair  time (%) = 3.09352 (14.8625)
            Neigh time (%) = 0.00725645 (0.0348627)
            Comm  time (%) = 12.9035 (61.9934)
            Outpt time (%) = 0.0834265 (0.400812)
            Other time (%) = 4.72661 (22.7084)

        , as a dictionary with the section (e.g. *Pair*) as Keyword and a list containing the time used [sec.]
        and percentage [%], as ``{'Pair': [149.62, 13.1], 'Bond': [16.504, 1.45], ...}``.

        :return: timing statistics
        :rtype: dict
        """
        if not self._timing:
            self._get_timing()
        return self._timing




class FixBlock(DataBlock):

    def __init__(self, blockFile, fline=0, lline=0, header_line='N/A'):
        super(FixBlock, self).__init__(blockFile, fline, lline, header_line)
        self.blockHeaderData = {}

    def info(self):
        super(FixBlock, self).info()
        for key,value in self.blockHeaderData.items():
            print key,':',value


