# -*- coding: utf-8 -*-

import logging

import joblib

__all__ = [
    'dump_pipe',
    'load_pipe',
]


def dump_pipe(pipe, filename, compress=True):
    """Dump this pipe on file using JobLib.

    :param pipe: the Pipe inherited object to dump on file
    :param filename: the filename to use
    :param compress: is True use compressed file
    """
    logging.info('dumping: {} on {}'.format(pipe.name, filename))
    with open(filename, 'wb') as _file:
        joblib.dump(pipe, _file, compress=compress)


def load_pipe(filename):
    """Load pipe from file using JobLib.

    :param filename: the filename to load
    """
    logging.info('loading: {}'.format(filename))
    with open(filename, 'rb') as _file:
        return joblib.load(_file)
