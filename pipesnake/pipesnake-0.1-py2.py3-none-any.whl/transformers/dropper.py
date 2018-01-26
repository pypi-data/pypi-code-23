# -*- coding: utf-8 -*-

import logging

import pandas

from pipesnake.base import Transformer
from pipesnake.base.utils import _shape

__all__ = [
    'DropDuplicates',
    'DropNanCols',
    'DropNanRows',
]


class DropDuplicates(Transformer):
    """Drop duplicated rows and/or cols.

    Args:
        :param on_rows: remove duplicated rows (default: `True`)
        :param on_cols: remove duplicated columns (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> dropper = DropDuplicates()
    >>> x_new, y_new = dropper.fit_transform(x, y)
    """

    def __init__(self, on_rows=True, on_cols=True, on_x=True, on_y=False, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.on_rows = on_rows
        self.on_cols = on_cols
        self.on_x = on_x
        self.on_y = on_y
        self._drop_indices_row = []

    def fit_x(self, x):
        if not self.on_x:
            return self
        if self.on_rows:
            self._drop_indices_row.extend(x.index[x.duplicated()].tolist())
            self._drop_indices_row = list(set(self._drop_indices_row))
        return self

    def fit_y(self, y):
        if not self.on_y:
            return self
        if self.on_rows:
            self._drop_indices_row.extend(y.index[y.duplicated()].tolist())
            self._drop_indices_row = list(set(self._drop_indices_row))
        return self

    def _transform(self, data, on_cols):
        _data = data.copy()
        if len(self._drop_indices_row) > 0:
            _data.drop(self._drop_indices_row, inplace=True)
        if self.on_cols and on_cols:
            _data = _data.T.drop_duplicates()
            _data = _data.T
        self.logging('  shape: {}'.format(_shape(_data)), level=logging.DEBUG)
        return _data

    def transform_x(self, x):
        self.logging('x shape: {}'.format(_shape(x)), level=logging.DEBUG)
        return self._transform(x, self.on_x)

    def transform_y(self, y):
        self.logging('y shape: {}'.format(_shape(y)), level=logging.DEBUG)
        return self._transform(y, self.on_y)

    def inverse_transform_x(self, x):
        self.logging('removing x duplicates is not invertible as transformation', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('removing y duplicates is not invertible as transformation', level=logging.WARNING)
        return y


class DropNanCols(Transformer):
    """Drop cols with nans.

    Args:
        :param how: 'any' if any NA values are present, 'all' if all values are NA (default: `'any'`). More details: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.dropna.html
        :param on_x: apply on `x` (default: `True`)
        :param on_y: apply on `y` (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> dropper = DropNanCols()
    >>> x_new, y_new = dropper.fit_transform(x, y)
    """

    def __init__(self, how='any', on_x=True, on_y=True, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.how = how
        self.on_x = on_x
        self.on_y = on_y

    def fit_x(self, x):
        return self

    def fit_y(self, y):
        return self

    def _transform(self, data):
        _data = data.copy()
        _data.dropna(axis=1, how=self.how, inplace=True)
        self.logging('  shape: {}'.format(_shape(_data)), level=logging.DEBUG)
        return _data

    def transform_x(self, x):
        if not self.on_x:
            return x
        self.logging('x shape: {}'.format(_shape(x)), level=logging.DEBUG)
        return self._transform(x)

    def transform_y(self, y):
        if not self.on_y:
            return y
        self.logging('y shape: {}'.format(_shape(y)), level=logging.DEBUG)
        return self._transform(y)

    def inverse_transform_x(self, x):
        self.logging('removing nan cols in x is not invertible as transformation', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('removing nan cols y is not invertible as transformation', level=logging.WARNING)
        return y


class DropNanRows(Transformer):
    """Drop rows with `any` or `all` nans.

    Args:
        :param how: 'any' if any NA values are present, 'all' if all values are NA (default: `'any'`) More details: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.dropna.html
        :param on_x: apply on `x` (default: `True`)
        :param on_y: apply on `y` (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> dropper = DropNanRows()
    >>> x_new, y_new = dropper.fit_transform(x, y)
    """

    def __init__(self, how='any', on_x=True, on_y=True, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.how = how
        self.on_x = on_x
        self.on_y = on_y
        self._drop_indices = []

    def _fit(self, data, apply):
        if apply:
            if self.how == 'any':
                self._drop_indices.extend(pandas.isnull(data).any(axis=1).nonzero()[0].tolist())
            if self.how == 'all':
                self._drop_indices.extend(pandas.isnull(data).all(axis=1).nonzero()[0].tolist())
            self._drop_indices = list(set(self._drop_indices))  # remove duplicates

    def fit_x(self, x):
        self._fit(x, self.on_x)
        return self

    def fit_y(self, y):
        self._fit(y, self.on_y)
        return self

    def _transform(self, data):
        _data = data.copy()
        _data.drop(self._drop_indices, inplace=True)
        self.logging('  shape: {}'.format(_shape(_data)), level=logging.DEBUG)
        return _data

    def transform_x(self, x):
        self.logging('x shape: {}'.format(_shape(x)), level=logging.DEBUG)
        return self._transform(x)

    def transform_y(self, y):
        self.logging('y shape: {}'.format(_shape(y)), level=logging.DEBUG)
        return self._transform(y)

    def inverse_transform_x(self, x):
        self.logging('removing nan rows in x is not invertible as transformation', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('removing nan rows y is not invertible as transformation', level=logging.WARNING)
        return y
