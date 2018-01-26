# -*- coding: utf-8 -*-

import logging

import pandas

from pipesnake.base import Transformer
from pipesnake.base.utils import _check_cols

__all__ = [
    'Combiner',
    'Roller',
]


class Combiner(Transformer):
    """Apply user function to a column or a set of columns

    This :class:`Transformer` applies `func` to the provided list of columns or list of lists of columns.

    Args:
        :param x_cols: a list of columns name or a list of indices (or list of lists for multi-parameter func)
        :param y_cols: a list of columns name or a list of indices (or list of lists for multi-parameter func)
        :param func: the functor for the function to be applied
        :param inv_func: the functor for the inverse function to be applied
        :param as_dataframe: boolean if true the subset dataframe is passed to func (default: `False`) and the function
                             is expected to return a DataFrame
        :param reset_index: if true when the results of transformers get concatenated
                            the index are reset otherwise the original index is kept (default: `True`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> def mult(x, y):
    >>>     return x * y
    >>> combiner = Combiner(x_cols=[[2, 3], [5, 7]], func=mult)
    >>> # This will return 2 columns where each item is the combination (multiplication) of
    >>> # items taken from the provided columns
    >>> x_new, y_new = combiner.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], func=None, inv_func=None, as_dataframe=False, reset_index=True,
                 sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.func = func
        self.inv_func = inv_func
        self.as_dataframe = as_dataframe
        self.reset_index = reset_index

        # this is need to inverse mapping
        self._inverse_map_column_names = {'x': {}, 'y': {}}

    def _check_signature(self, cols):
        # check if func signature match the number of inputs
        func_signature = self.func.__code__.co_varnames
        for c in cols:
            dim = 1
            if type(c) == list:
                dim = len(c)
            assert len(func_signature) >= dim, 'mismatch number function params {} and number of inputs {}'.format(
                func_signature, c)

    def fit_x(self, x):
        self._check_signature(self.x_cols)
        existing_columns = x.columns.values.tolist()
        for cols in self.x_cols:
            if type(cols) == list:
                for c in cols:
                    assert c in existing_columns, 'column: {} not in x columns {}'.format(c, existing_columns)
            else:
                assert cols in existing_columns, 'column: {} not in x columns {}'.format(cols, existing_columns)
        return self

    def fit_y(self, y):
        self._check_signature(self.y_cols)
        existing_columns = y.columns.values.tolist()
        for cols in self.y_cols:
            if type(cols) == list:
                for c in cols:
                    assert c in existing_columns, 'column: {} not in y columns'.format(c)
            else:
                assert cols in existing_columns, 'column: {} not in y columns'.format(cols)
        return self

    def _transform(self, data, cols, proc_x=True):
        """ The actual implementation transformer

        Args:
            :param data: a pandas dataframe to be processed
            :param cols: the list of columns to be processed
            :param proc_x: if true transform `x` otherwise transform `y`
        Returns:
            :return data_new: the transformed data
        """

        # nothing to do
        if self.func is None:
            return data
        if len(cols) == 0:
            return data

        data_new = pandas.DataFrame()
        for c in cols:
            if type(c) != list:
                c = [c]
            self.logging('applying {} to {} columns'.format(self.func.__name__, c), level=logging.DEBUG)
            _x = data[c].copy()
            if type(_x) == pandas.Series:
                _x = _x.to_frame()
            if self.as_dataframe:
                data_curr = self.func(_x)
            else:
                res = []
                for _, r in _x.iterrows():
                    res.append(self.func(*r))
                data_curr = pandas.DataFrame(res)

            curr_column_name = self.func.__name__ + '_' + '_'.join([str(i) for i in c])
            data_curr.columns = [curr_column_name]

            if proc_x:
                self._inverse_map_column_names['x'][curr_column_name] = c
            else:
                self._inverse_map_column_names['y'][curr_column_name] = c

            # concatenate columns
            join = True
            if data_new.empty:
                data_new = data_curr.copy()
                if self.reset_index:
                    data_new.reset_index(inplace=True)
                data_new.drop(['index'], axis=1, inplace=True)
                join = False
            if join:
                if self.reset_index:
                    data_curr.reset_index(inplace=True)
                data_curr.drop(['index'], axis=1, inplace=True)
                data_new = data_new.join(data_curr)

        return data_new

    def transform_x(self, x):
        return self._transform(x, self.x_cols)

    def transform_y(self, y):
        return self._transform(y, self.y_cols, proc_x=False)

    def _inverse_transform(self, data, proc_x=True):
        """ The actual implementation of inverse transform

        Args:
            :param data:
            :param proc_x:
        """

        # nothing to do
        if self.inv_func is None:
            return data
        if proc_x and len(self._inverse_map_column_names['x']) == 0:
            return data
        if not proc_x and len(self._inverse_map_column_names['y']) == 0:
            return data

        if proc_x:
            cols = self._inverse_map_column_names['x']
        else:
            cols = self._inverse_map_column_names['y']

        data_org = pandas.DataFrame()
        for col, org_cols in cols.items():
            self.logging('inverting from {} to {} columns using {}'.format(col, org_cols, self.inv_func.__name__),
                         level=logging.DEBUG)
            _t = data[col].copy().to_frame()
            if type(_t) == pandas.Series:
                _t = _t.to_frame()
            if self.as_dataframe:
                data_curr = self.inv_func(_t)
            else:
                res = []
                for _, r in _t.iterrows():
                    res.append(self.inv_func(*r))
                data_curr = pandas.DataFrame(res)
            if type(org_cols) != list:
                org_cols = [org_cols]
            data_curr.columns = org_cols
            logging.debug('expected cols: {}'.format(org_cols))
            logging.debug('current cols: {}'.format(data_curr.columns.values.tolist()))
            assert len(org_cols) == len(
                data_curr.columns.values.tolist()), 'mismatch number of cols {} expected {}'.format(
                len(org_cols), len(data_curr.columns.values.tolist()))

            # concatenate columns
            join = True
            if data_org.empty:
                data_org = data_curr.copy()
                if self.reset_index:
                    data_org.reset_index(inplace=True)
                data_org.drop(['index'], axis=1, inplace=True)
                join = False
            if join:
                if self.reset_index:
                    data_curr.reset_index(inplace=True)
                data_curr.drop(['index'], axis=1, inplace=True)
                data_org = data_org.join(data_curr)

        return data_org

    def inverse_transform_x(self, x):
        return self._inverse_transform(x)

    def inverse_transform_y(self, y):
        return self._inverse_transform(y, proc_x=False)


class Roller(Combiner):
    """Apply the provided function rolling within a given window

    Note: resulting columns may contain nan (typically a total of `window-1` at the beginning)

    Args:
        :param x_cols: a list of columns name or a list of indices (or list of lists for multi-parameter func)
        :param y_cols: a list of columns name or a list of indices (or list of lists for multi-parameter func)
        :param func: the functor for the function to be applied (default: `None`)
        :param inv_func: the functor for the inverse function to be applied (default: `None`)
        :param window: an integer indicating the window size (default: `3`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> roller = Roller(x_cols=[0], roll_func=lambda x: x[0] + x[1], window=2)
    >>> x_new, y_new = roller.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], roll_func=None, inv_roll_func=None, window=3, sklearn_output=False,
                 name=None):
        Combiner.__init__(self, x_cols=x_cols, y_cols=y_cols, func=self.roller_func, inv_func=self.roller_inv_func,
                          as_dataframe=True, sklearn_output=sklearn_output, name=name)
        self.roll_func = roll_func
        self.inv_roll_func = inv_roll_func
        self.window = window

    def roller_func(self, data):
        return data.rolling(window=self.window).apply(self.roll_func)

    def roller_inv_func(self, data):
        return data.rolling(window=self.window).apply(self.inv_roll_func)

    def fit_x(self, x):
        Combiner._check_signature(self, self.x_cols)
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        return self

    def fit_y(self, y):
        Combiner._check_signature(self, self.y_cols)
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        return self
