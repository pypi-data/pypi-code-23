#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


class Table(object):
    """
    A class to store, write to file, or manage a 2D data table.

    :param data_in: 2D numpy array
    :type data_in: numpy.ndarray
    :param props: list of properties as strings
    :type props: list
    """

    def __init__(self, data_in=None, props=None):
        self._data = None
        self._properties = None
        self._units = None
        if data_in is not None:
           self.addData(data_in)
        if props is not None:
            self.setProperties(props)


    def addData(self, data_in):
        """
        Populate or extend the data table.

        The input have to be a 2-dimensional `(m,n)` numpy array, according to the convention,
        stored `m` rows of `n` columns.

        :param data: 2D numpy array
        :type data_in: np.ndarray
        """
        if type(data_in) is not np.ndarray:
            raise TypeError('data_in must be of type numpy.ndarray')
        if data_in.ndim is 1:
            data_in = np.array([ data_in ])
        if data_in.ndim is not 2:
            raise TypeError('data_in must be a 2D numpy array')
        if self.shape  is not None and self.shape[1] is not data_in.shape[1]:
            raise TypeError(str("data_in must be a numpy array of shape (*,{0:d})".format(self.shape[1])))
        if self._data:
            self._data = np.vstack((self._data, data_in))
        else:
            self._data = data_in


    def setProperties(self, props):
        """
        Set the name of the columns by a list of strings.

        :param props: list of properties as strings
        :type props: list
        """
        if type(props) is not list:
            raise TypeError('props must be of type list.')
        if not any(isinstance(x, str) for x in props):
            raise TypeError('props list must contain strings.')
        if self.shape is not None and self.shape[1] is not len(props):
            raise TypeError(str("props must be a list of length {0:d}".format(self.shape[1])))
        self._properties = props


    def write(self, filename):
        """
        Writes the whole table to a file.

        :param filename: output file name
        :type filename: str
        """
        np.savetxt(filename, self._data, fmt='%+1.8e', delimiter=' ',
                   newline='\n', header=self.header_line, comments='# ')

    @property
    def properties(self):
        return self._properties

    @property
    def header_line(self):
        if self._properties is not None:
            return ' '.join(self._properties)
        else:
            return None


    @property
    def shape(self):
        """ Tuple of table dimensions, like `(100,5)` for a table containing 100 rows and 5 columns."""
        if self._data is not None:
            return self._data.shape
        elif self._properties is not None:
            return tuple((0, len(self._properties)))
        else:
            return None

    @property
    def array(self):
        """ Returns the data as a 2D numpy array,"""
        return self._data


    def __len__(self):
        if self.shape is not None:
            return self.shape[1]
        else:
            return None
