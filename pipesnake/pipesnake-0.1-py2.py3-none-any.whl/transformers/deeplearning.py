# -*- coding: utf-8 -*-
import logging

import numpy

from pipesnake.base import Transformer

__all__ = [
    'LSTMPacker',
]


class LSTMPacker(Transformer):
    """Pack rows in order to be used as input for LSTM networks.

    Args:
        :param sequence_len: the size of the sequences to be created (default: `2`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> packer = LSTMPacker(sequence_len=10)
    >>> x_new, y_new = packer.fit_transform(x, y)
    """

    def __init__(self, sequence_len=2, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.sequence_len = sequence_len

    def fit_x(self, x):
        assert type(x) == numpy.ndarray, 'x needs to be a numpy array, got: {}'.format(type(x))
        return self

    def fit_y(self, y):
        assert type(y) == numpy.ndarray, 'y needs to be a numpy array, got: {}'.format(type(y))
        return self

    def transform_x(self, x):
        data = []
        for i in range(x.shape[0] - self.sequence_len):
            data.append(x[i:i + self.sequence_len])
        return numpy.asarray(data)

    def transform_y(self, y):
        return y[self.sequence_len:]

    def inverse_transform_x(self, x):
        self.logging('LSTMPacker on x is not invertible', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('LSTMPacker on x is not invertible', level=logging.WARNING)
        return y
