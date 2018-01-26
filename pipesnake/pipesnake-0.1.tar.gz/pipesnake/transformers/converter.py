# -*- coding: utf-8 -*-
import logging

import pandas

from pipesnake.base import Transformer
from pipesnake.base.utils import _check_cols

__all__ = [
    'Category2Number',
]


class Category2Number(Transformer):
    """Convert categorical to number.

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param skipna: if True the null values (None, NaN, ...) will not be replaced (default: `False`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> cat2num = Category2Number(x_cols=['x_1'], y_cols=['y_1'])
    >>> x_new, y_new = cat2num.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], skipna=False, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.skipna = skipna
        self._map_category_to_number = {'x': {}, 'y': {}}
        self._map_number_to_category = {'x': {}, 'y': {}}

    def _fit(self, data, cols):
        cat_to_num = {}
        num_to_cat = {}
        for c in cols:
            cat_to_num[c] = {}
            num_to_cat[c] = {}
            uniques = sorted(data[c].unique().tolist())
            for i, v in enumerate(uniques):
                if pandas.isnull(v):
                    if self.skipna:
                        continue
                    else:
                        cat_to_num[c]['_nan_'] = i
                        num_to_cat[c][i] = pandas.np.nan
                else:
                    cat_to_num[c][v] = i
                    num_to_cat[c][i] = v
        return cat_to_num, num_to_cat

    def fit_x(self, x):
        """Create the list of columns to be converted for `x` and related mappings.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Return:
            :param self:
        """
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        self._map_category_to_number['x'], self._map_number_to_category['x'] = self._fit(x, self.x_cols)
        return self

    def fit_y(self, y):
        """Create the list of columns to be converted for `y` and related mappings.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Return:
            :param self:
        """
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        self._map_category_to_number['y'], self._map_number_to_category['y'] = self._fit(y, self.y_cols)
        return self

    def _transform(self, data, cols, cat_to_num):
        if len(cols) == 0:
            return data
        _data = data.copy()
        if not self.skipna:
            _data[cols].fillna(value='_nan_', inplace=True)
        for c in cols:
            _data.replace(to_replace={c: cat_to_num[c]}, inplace=True)
        return _data

    def transform_x(self, x):
        self.logging('x category to number: {}'.format(self._map_category_to_number['x']), level=logging.DEBUG)
        return self._transform(x, self.x_cols, self._map_category_to_number['x'])

    def transform_y(self, y):
        self.logging('y category to number: {}'.format(self._map_category_to_number['y']), level=logging.DEBUG)
        return self._transform(y, self.y_cols, self._map_category_to_number['y'])

    def _inverse_transform(self, data, cols, num_to_cat):
        if len(cols) == 0:
            return data
        _data = data.copy()
        for c in cols:
            _data.replace(to_replace={c: num_to_cat[c]}, inplace=True)
        return _data

    def inverse_transform_x(self, x):
        self.logging('x number to category: {}'.format(self._map_number_to_category['x']), level=logging.DEBUG)
        return self._inverse_transform(x, self.x_cols, self._map_number_to_category['x'])

    def inverse_transform_y(self, y):
        self.logging('y number to category: {}'.format(self._map_number_to_category['y']), level=logging.DEBUG)
        return self._inverse_transform(y, self.y_cols, self._map_number_to_category['y'])
