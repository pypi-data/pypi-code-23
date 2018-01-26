# -*- coding: utf-8 -*-

import logging
import math

from pipesnake.base import Transformer

__all__ = [
    'ToNumpy',
    'ColumnRenamer',
    'Copycat',
]


class ToNumpy(Transformer):
    """Convert `x` and `y` to a particular numpy type.

    The common case is that once you have your data pipeline you need to make it
    compatible with numpy so that scikit-learn can use it without any issue.
    Typically this transformer is the last one in the pipelines so that the output
    is ready to feed a scikit-learn pipeline.

    Note: this will not `y.ravel()` as far in pipesnake also target can be a matrix

    Args:
        :param as_type: is the final type you want to convert the dataframes (default: `float`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> astype = ToNumpy(as_type=int)
    >>> x_new, y_new = astype.fit_transform(x, y)
    """

    def __init__(self, as_type=float, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.as_type = as_type

    def fit_x(self, x):
        return self

    def fit_y(self, y):
        return self

    def _transform(self, data):
        _data = data.copy()
        return _data.astype(self.as_type).as_matrix()

    def transform_x(self, x):
        return self._transform(x)

    def transform_y(self, y):
        return self._transform(y)

    def inverse_transform_x(self, x):
        self.logging('type casting on x is not invertible as transformation', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('type casting on x is not invertible as transformation', level=logging.WARNING)
        return y


class ColumnRenamer(Transformer):
    """Rename `x` and `y` columns.

    Args:
        :param prefix: prefix for column names (default: `''`)
        :param postfix: postfix for column names (default: `''`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> renamer = ColumnRenamer()
    >>> x_new, y_new = renamer.fit_transform(x, y)
    """

    def __init__(self, prefix='', postfix='', sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.prefix = prefix
        self.postfix = postfix
        # this is need to inverse mapping
        self._original_column_names = {'x': {}, 'y': {}}
        self._new_column_names = {'x': {}, 'y': {}}

    def _fit(self, data, col_name):
        original_names = data.columns.values.tolist()
        dim = len(original_names)
        pad = int(math.ceil(math.log10(float(dim))))
        base_name = self.prefix + col_name + '{}' + self.postfix
        new_names = [base_name.format(str(i).zfill(pad)) for i in range(dim)]
        return original_names, new_names

    def fit_x(self, x):
        self._original_column_names['x'], self._new_column_names['x'] = self._fit(x, 'x_')
        return self

    def fit_y(self, y):
        self._original_column_names['y'], self._new_column_names['y'] = self._fit(y, 'y_')
        return self

    def transform_x(self, x):
        _x = x.copy()
        _x.columns = self._new_column_names['x']
        self.logging('x new column names: {}'.format(self._new_column_names['x']), level=logging.DEBUG)
        return _x

    def transform_y(self, y):
        _y = y.copy()
        _y.columns = self._new_column_names['y']
        self.logging('y new column names: {}'.format(self._new_column_names['y']), level=logging.DEBUG)
        return _y

    def inverse_transform_x(self, x):
        _x = x.copy()
        _x.columns = self._original_column_names['x']
        self.logging('x original column names: {}'.format(self._original_column_names['x']), level=logging.DEBUG)
        return _x

    def inverse_transform_y(self, y):
        _y = y.copy()
        _y.columns = self._original_column_names['y']
        self.logging('y original column names: {}'.format(self._original_column_names['y']), level=logging.DEBUG)
        return _y


class Copycat(Transformer):
    """Copy the datasets forward.

    This is typically used to replicate dataset inside :class:`ParallelPipe` to augment features and/or targets.

    Args:
        :param on_x: apply on `x` (default: `True`)
        :param on_y: apply on `y` (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`
    """

    def __init__(self, on_x=True, on_y=True, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.on_x = on_x
        self.on_y = on_y

    def fit_x(self, x):
        return self

    def fit_y(self, y):
        return self

    def transform_x(self, x):
        if not self.on_x:
            return None
        return x.copy()

    def transform_y(self, y):
        if not self.on_y:
            return None
        return y.copy()

    def inverse_transform_x(self, x):
        self.logging('copying x is not invertible', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('copying x is not invertible', level=logging.WARNING)
        return y
