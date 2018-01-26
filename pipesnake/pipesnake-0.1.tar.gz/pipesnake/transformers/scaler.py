# -*- coding: utf-8 -*-

import logging

import numpy

from pipesnake.base import Transformer
from pipesnake.base.utils import _check_cols

__all__ = [
    'MinMaxScaler',
    'StdScaler',
    'MadScaler',
    'UnitLenghtScaler',
]


class MinMaxScaler(Transformer):
    """Min max scaler.

    This will scale the data (by columns) to fit [min; max] interval.

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param min_value: min value after scaling (default: `1.0`)
        :param max_value: max value after scaling (default: `1.0`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> scaler = MinMaxScaler(x_cols=['x_1'], y_cols=['y_1'])
    >>> x_new, y_new = scaler.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], min_value=-1.0, max_value=1.0, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.min_value = min_value
        self.max_value = max_value
        self._d = self.max_value - self.min_value
        # the inverse mapping is needed to invert the transformation
        self._inverse_map = {'x': None, 'y': None}

    def fit_x(self, x):
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        return self

    def fit_y(self, y):
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        return self

    def transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        _x = x.copy()
        self._inverse_map['x'] = (_x[self.x_cols].min(), _x[self.x_cols].max())
        _x[self.x_cols] = (_x[self.x_cols] - _x[self.x_cols].min()) / (
            _x[self.x_cols].max() - _x[self.x_cols].min()) * self._d + self.min_value
        return _x

    def transform_y(self, y):
        if len(self.y_cols) == 0:
            return y
        _y = y.copy()
        self._inverse_map['y'] = (_y[self.y_cols].min(), _y[self.y_cols].max())
        _y[self.y_cols] = (_y[self.y_cols] - _y[self.y_cols].min()) / (
            _y[self.y_cols].max() - _y[self.y_cols].min()) * self._d + self.min_value
        return _y

    def inverse_transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        _x = x.copy()
        _min, _max = self._inverse_map['x']
        _x[self.x_cols] = (_x[self.x_cols] - self.min_value) / self._d * (_max - _min) + _min
        return _x

    def inverse_transform_y(self, y):
        if len(self._y_cols) == 0:
            return y
        _y = y.copy()
        _min, _max = self._inverse_map['y']
        _y[self.y_cols] = (_y[self.y_cols] - self.min_value) / self._d * (_max - _min) + _min
        return _y


class StdScaler(Transformer):
    """Standard deviation scaler.

    This will scale the data (by columns) following x' = ( x - mean(X) ) / ( k * std(X) ).

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param k: is a scaling factor for the standard deviation (default: `3.0`)
        :param skipna: exclude NA/null values when computing the result (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> scaler = StdScaler(x_cols=['x_1'], y_cols=['y_1'])
    >>> x_new, y_new = scaler.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], k=3.0, skipna=True, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.k = k
        self.skipna = skipna
        # the inverse mapping is needed to invert the transformation
        self._inverse_map = {'x': {}, 'y': {}}

    def fit_x(self, x):
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        return self

    def fit_y(self, y):
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        return self

    def transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        _x = x.copy()
        _mean = _x[self.x_cols].mean(skipna=self.skipna)
        _std = _x[self.x_cols].std(skipna=self.skipna)
        self._inverse_map['x'] = (_mean, _std)
        _x[self.x_cols] = (_x[self.x_cols] - _mean) / (self.k * _std)
        return _x

    def transform_y(self, y):
        if len(self.y_cols) == 0:
            return y
        _y = y.copy()
        _mean = _y[self.y_cols].mean(skipna=self.skipna)
        _std = _y[self.y_cols].std(skipna=self.skipna)
        self._inverse_map['y'] = (_mean, _std)
        _y[self.y_cols] = (_y[self.y_cols] - _mean) / (self.k * _std)
        return _y

    def inverse_transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        _x = x.copy()
        _mean, _std = self._inverse_map['x']
        _x[self.x_cols] = _x[self.x_cols] * self.k * _std + _mean
        return _x

    def inverse_transform_y(self, y):
        if len(self.y_cols) == 0:
            return y
        _y = y.copy()
        _mean, _std = self._inverse_map['y']
        _y[self.y_cols] = _y[self.y_cols] * self.k * _std + _mean
        return _y


class MadScaler(Transformer):
    """Median absolute deviation scaler.

    This will scale the data (by columns) following x' = ( x - median(X) ) / ( k * mad(X) ).

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param k: is a scaling factor for the standard deviation (default: `3.0`)
        :param skipna: exclude NA/null values when computing the result (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> scaler = MadScaler(x_cols=['x_1'], y_cols=['y_1'])
    >>> x_new, y_new = scaler.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], k=3.0, skipna=True, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.k = k
        self.skipna = skipna
        # the inverse mapping is needed to invert the transformation
        self._inverse_map = {'x': {}, 'y': {}}

    def fit_x(self, x):
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        return self

    def fit_y(self, y):
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        return self

    def transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        _x = x.copy()
        _median = _x[self.x_cols].median(skipna=self.skipna)
        _mad = _x[self.x_cols].mad(skipna=self.skipna)
        self._inverse_map['x'] = (_median, _mad)
        _x[self.x_cols] = (_x[self.x_cols] - _median) / (self.k * _mad)
        return _x

    def transform_y(self, y):
        if len(self.y_cols) == 0:
            return y
        _y = y.copy()
        _median = _y[self.y_cols].median(skipna=self.skipna)
        _mad = _y[self.y_cols].mad(skipna=self.skipna)
        self._inverse_map['y'] = (_median, _mad)
        _y[self.y_cols] = (_y[self.y_cols] - _median) / (self.k * _mad)
        return _y

    def inverse_transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        _x = x.copy()
        _median, _mad = self._inverse_map['x']
        _x[self.x_cols] = _x[self.x_cols] * self.k * _mad + _median
        return _x

    def inverse_transform_y(self, y):
        if len(self.y_cols) == 0:
            return y
        _y = y.copy()
        _median, _mad = self._inverse_map['y']
        _y[self.y_cols] = _y[self.y_cols] * self.k * _mad + _median
        return _y


class UnitLenghtScaler(Transformer):
    """Scale the feature vector to have norm 1.0.

    This will scale the data (by row) following X' = X / norm(X).

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param invertible: if true collect additional data make the transformer invertible. Note that
                           this requires to store one value for each row in `x` and `y` (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this transformer

    Examples:

    >>> scaler = UnitLenghtScaler()
    >>> x_new, y_new = scaler.fit_transform(x, y)
    """

    def __init__(self, x_cols='all', y_cols=[], invertible=True, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.invertible = invertible
        # the inverse mapping is needed to invert the transformation
        self._inverse_map = {'x': None, 'y': None}

    def fit_x(self, x):
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        return self

    def fit_y(self, y):
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        return self

    def transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        _x = x.copy()
        n = numpy.sqrt(numpy.square(_x[self.x_cols]).sum(axis=1))
        if self.invertible:
            self._inverse_map['x'] = n
        _x[self.x_cols] = _x[self.x_cols].div(n, axis=0)
        return _x

    def transform_y(self, y):
        if len(self.y_cols) == 0:
            return y
        _y = y.copy()
        n = numpy.sqrt(numpy.square(_y[self.y_cols]).sum(axis=1))
        if self.invertible:
            self._inverse_map['y'] = n
        _y[self.y_cols] = _y[self.y_cols].div(n, axis=0)
        return _y

    def inverse_transform_x(self, x):
        if len(self.x_cols) == 0:
            return x
        if not self.invertible:
            self.logging('the transformer has not been set to be invertible, you should set invertible=True',
                         level=logging.WARNING)
            return x
        _x = x.copy()
        _x[self.x_cols] = _x[self.x_cols].mul(self._inverse_map['x'], axis=0)
        return _x

    def inverse_transform_y(self, y):
        if len(self.y_cols) == 0:
            return y
        if not self.invertible:
            self.logging('the transformer has not been set to be invertible, you should set invertible=True',
                         level=logging.WARNING)
            return y
        _y = y.copy()
        _y[self.y_cols] = _y[self.y_cols].mul(self._inverse_map['y'], axis=0)
        return _y
