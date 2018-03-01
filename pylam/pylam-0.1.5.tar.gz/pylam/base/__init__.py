# -*- coding: utf-8 -*-
"""
This module contains base classes and common functions.

.. note:: To access the classes and functions in this module, you need to extend the lib by importing ``pylam.base``.

"""

from .table import Table
from .indexedfile import IndexedFile
from .blockfile import (BlockFile, Block)

__all__ = ( 'Table', 'IndexedFile', 'BlockFile', 'Block')


import numpy as np
import tableprint


def zeroTable(ncols, nrows, props=None):
    """Creates a table containing zeros, like :func:`numpy.zeros`.

    :param ncols: number of columns
    :type ncols: int
    :param nrows: number of rows
    :type  nrows: int
    :param props: list of properties as strings
    :type props: list
    :return: Table object
    :rtype: .Table
    """
    data_in = np.zeros((nrows, ncols))
    return Table(data_in, props=props)


def listOfStr2listOfFloats(list_of_str):
    """
    Converts a list of strings to a list of floats.

    :param list_of_str: list of strings
    :type list_of_str: list
    :return: list of floats
    :rtype: list
    """
    out = []
    for str in list_of_str:
        out.append( float(str) )
    return out


def listOfStr2listOfInts(list_of_str):
    """
    Converts a list of strings to a list of integers.

    :param list_of_str: list of strings
    :type list_of_str: list
    :return: list of integers
    :rtype: list
    """
    out = []
    for str in list_of_str:
        out.append( int(str) )
    return out


def dict2table(dict_in, headers=['keyword', 'value'], kworder=[], style='clean', width=11):
    data = []
    if len(kworder) > 0:
        for kw in kworder:
            data.append([kw, dict_in[kw]])
    else:
        for kw, val in dict_in.items():
            data.append([kw, val])
    tableprint.table(data, headers, style=style, width=width)
