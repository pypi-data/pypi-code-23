#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helper functions to handle data extraction sources."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


from contextlib import contextmanager
import gzip
import six
import struct
import sys

from . import _errors
from sciexp2.common.compat import StringIO


def get_file(arg):
    """Get a file-like object from `arg`."""
    if isinstance(arg, six.string_types):
        if arg.endswith(".gz"):
            return gzip.open(arg)
        else:
            return open(arg)
    else:
        return arg


def get_name(source, index):
    if isinstance(source, six.string_types):
        return source
    elif hasattr(source, "name"):
        return source.name
    elif index is None:
        return None
    else:
        return "number %d" % index


def get_size(source):
    with current_position(source):
        if isinstance(source, gzip.GzipFile):
            # little-endian unsigned integer in the last 4 bytes of the file
            source = source.myfileobj
            source.seek(0, 2)
            end_position = source.tell()
            assert end_position >= 4
            source.seek(-4, 2)
            return struct.unpack('<I', source.read(4))[0]
        else:
            source.seek(0, 2)
            return source.tell()


def is_empty(source):
    source_size = get_size(source)
    return source_size == 0


@contextmanager
def current_position(source):
    if isinstance(source, gzip.GzipFile):
        source = source.myfileobj
    source_pos = source.tell()
    yield
    source.seek(source_pos)

@contextmanager
def current_position_as_binary(source):
    if isinstance(source, gzip.GzipFile):
        source = source.myfileobj
    source_pos = source.tell()
    if hasattr(source, "name"):
        fobj = open(source.name, "rb")
    else:
        fobj = StringIO(source.read())
        source.seek(source_pos)
    fobj.seek(source_pos)
    yield fobj
    fobj.close()


__all__ = [
    "get_file", "get_name", "get_size", "is_empty", "check_empty",
    "current_position", "current_position_as_binary",
]
