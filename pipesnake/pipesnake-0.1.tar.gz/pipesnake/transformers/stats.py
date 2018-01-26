# -*- coding: utf-8 -*-

import logging

import numpy

from pipesnake.base import Transformer
from pipesnake.base.utils import _check_cols
from pipesnake.utils.decorator import memoize

__all__ = [
    'ToSymbolProbability',
]


@memoize
def get_pdf_value(hist, edges, pos):
    """Get the value of a pdf for a given x

    :param hist: list of histogram values
    :param edges: list of bins
    :param pos: position on the support
    :return: pdf value
    """
    ed = numpy.digitize(pos, edges).tolist()
    if ed > len(hist) - 1:
        return hist[-1]
    return hist[ed]


@memoize
def get_pdf_support(edges, pos):
    """As far as the support is quantized this maps a
    continuous value to a quantized one

    :param edges: list of bins
    :param pos: position on the support
    :return: quantized position
    """
    return edges[numpy.digitize(pos, edges).tolist()]


def build_support(x):
    """Build the support for the x pdf."""
    _x = numpy.sort(numpy.unique(x))
    _delta = numpy.median(numpy.diff(_x))
    _min = numpy.min(_x)
    _max = numpy.max(_x)
    return numpy.arange(_min - _delta, _max + _delta, _delta)


def build_pdf(x, density=True):
    """Compute the histogram (pdf) of the data"""
    hist, edges = numpy.histogram(x, bins=build_support(x), density=density)
    return hist, edges


class ToSymbolProbability(Transformer):
    """Convert values in columns to their probabilities.

    The transfomer estimate the histogram (`pdf`) for the provided columns and
    then convert original values to probability `x_new = pdf(x)`

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> topb = ToSymbolProbability(x_cols=['x_1'])
    >>> x_new, y_new = topb.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self._pdfs = {'x': {}, 'y': {}}

    def _fit(self, data, cols, pdf):
        for c in cols:
            self.logging(' {}'.format(c), level=logging.DEBUG)
            pdf[c] = build_pdf(data[c])

    def fit_x(self, x):
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        self.logging('fitting x', level=logging.DEBUG)
        self._fit(x, self.x_cols, self._pdfs['x'])
        return self

    def fit_y(self, y):
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        self.logging('fitting y', level=logging.DEBUG)
        self._fit(y, self.y_cols, self._pdfs['y'])
        return self

    def _transform(self, data, cols, pdf):
        _data = data.copy()
        for c in cols:
            self.logging(' {}'.format(c), level=logging.DEBUG)
            _data[c] = _data[c].apply(lambda x: get_pdf_value(pdf[c][0], pdf[c][1], x))
        return _data

    def transform_x(self, x):
        self.logging('transforming x', level=logging.DEBUG)
        return self._transform(x, self.x_cols, self._pdfs['x'])

    def transform_y(self, y):
        self.logging('transforming x', level=logging.DEBUG)
        return self._transform(y, self.y_cols, self._pdfs['y'])

    def inverse_transform_x(self, x):
        self.logging('ToSymbolProbability on x is not invertible', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('ToSymbolProbability on y is not invertible', level=logging.WARNING)
        return y
