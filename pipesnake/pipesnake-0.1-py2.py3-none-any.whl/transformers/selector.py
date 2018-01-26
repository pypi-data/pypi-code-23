# -*- coding: utf-8 -*-

import logging

from pipesnake.base import Transformer
from pipesnake.base.utils import _check_cols
from pipesnake.base.utils import _shape

__all__ = [
    'ColumnSelector',
]


class ColumnSelector(Transformer):
    """Select a given list of column names to keep

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> selector = ColumnSelector(x_cols=['column_A', 7], y_cols=[0])
    >>> # This will return an x DataFrame with only 'column_A' and the 8th column, and a y DataFrame
    >>> # with just the first column
    """

    def __init__(self, x_cols=[], y_cols=[], sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols

    def fit_x(self, x):
        """Create the list of columns to be kept for x.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Return:
            :param self:
        """
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        return self

    def fit_y(self, y):
        """Create the list of columns to be kept for y.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Return:
            :param self:
        """
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        return self

    def transform_x(self, x):
        """Transform x just dropping irrelevant columns.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:s
            :return x_new: the new transformed x
        """
        if len(self.x_cols) == 0:
            return x
        self.logging('x shape: {}'.format(_shape(x)), level=logging.DEBUG)
        x_new = x.copy()
        if len(self.x_cols) > 0:
            x_new.drop(list(set(x_new.columns.values.tolist()) - set(self.x_cols)), axis=1, inplace=True)
        self.logging(' shape: {}'.format(_shape(x_new)), level=logging.DEBUG)
        return x_new

    def transform_y(self, y):
        """Transform y just dropping irrelevant columns.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_new: the new transformed y
        """
        if len(self.y_cols) == 0:
            return y
        self.logging('y shape: {}'.format(_shape(y)), level=logging.DEBUG)
        y_new = y.copy()
        if len(self.y_cols) > 0:
            y_new.drop(list(set(y_new.columns.values.tolist()) - set(self.y_cols)), axis=1, inplace=True)
        self.logging('  shape: {}'.format(_shape(y_new)), level=logging.DEBUG)
        return y_new

    def inverse_transform_x(self, x):
        """Removing columns is not invertible as transformation.

        Returns:
            :return x: no inverse transform is applied
        """
        self.logging('removing x columns is not invertible as transformation', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        """Removing columns is not invertible as transformation.

        Returns:
            :return y: no inverse transform is applied
        """
        self.logging('removing y columns is not invertible as transformation', level=logging.WARNING)
        return y
