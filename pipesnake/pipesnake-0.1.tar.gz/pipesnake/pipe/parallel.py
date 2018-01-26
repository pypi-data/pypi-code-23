# -*- coding: utf-8 -*-

import logging

import pandas

from pipesnake.base import Pipe
from pipesnake.base import Transformer
from pipesnake.utils.decorator import memory
from pipesnake.utils.decorator import timeit

__all__ = [
    'ParallelPipe',
]


class ParallelPipe(Pipe, Transformer):
    """:class:`ParallelPipe` applies a list of transformers as parallel.

    The class itself inherits from :class:`Pipe` and :class:`Transformer` so that it is possible
    to use this as :class:`Transformer` objects.

    Args:
        :param transformers: a list of :class:`Transformer` objects
        :param reset_index: if true when the results of transformers get concatenated
                                the index are reset otherwise the original index is kept
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline
        :param name: name for this :class:`Transformer`
    """

    def __init__(self, transformers=[], reset_index=True, sklearn_output=False, name=None):
        Pipe.__init__(self, transformers=transformers)
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.reset_index = reset_index
        self._original_column_names = {'x': {}, 'y': {}}

    @memory
    @timeit
    def fit_x(self, x):
        """Fit all transformers parameters in the pipe.

        This function apply `fit_x` for each transformer in the pipe.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return self:

        .. todo:: This can be parallelized in computation
        """
        self.logging('fitting x...')
        self._original_column_names['x'] = x.columns
        for t in self.transformers:
            self.logging('-> {}'.format(t.name))
            t.fit_x(x)
        return self

    @memory
    @timeit
    def fit_y(self, y):
        """Fit all transformers parameters in the pipe.

        This function apply `fit_y` for each transformer in the pipe.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return self:

        .. todo:: This can be parallelized in computation
        """
        self.logging('fitting y...')
        self._original_column_names['y'] = y.columns
        for t in self.transformers:
            self.logging('-> {}'.format(t.name))
            t.fit_y(y)
        return self

    def _transform(self, data, proc_x=True):
        """ The actual implementation transformer

        Args:
            :param data: a pandas dataframe
            :param proc_x: if true transform `x` otherwise transform `y`
        Returns:
            :return data_new: the transformed data

        .. todo:: This can be parallelized in computation
        """

        # nothing to do
        if len(self.transformers) == 0:
            return data

        data_new = pandas.DataFrame()
        for t in self.transformers:
            self.logging('-> {}'.format(t.name))
            if proc_x:
                data_curr = t.transform_x(data)
            else:
                data_curr = t.transform_y(data)
            if data_curr is None or data_curr.empty:
                continue

            join = True
            if data_new.empty:
                data_new = data_curr.copy()
                if self.reset_index:
                    data_new.reset_index(inplace=True)
                data_new.drop(['index'], axis=1, inplace=True)
                data_new.columns = [c + '_{}'.format(t.name) for c in data_new.columns]
                join = False

            if join:
                if self.reset_index:
                    data_curr.reset_index(inplace=True)
                data_curr.drop(['index'], axis=1, inplace=True)
                data_curr.columns = [c + '_{}'.format(t.name) for c in data_curr.columns]
                data_new = data_new.join(data_curr)

        return data_new

    @memory
    @timeit
    def transform_x(self, x):
        """Transform `x`.

        This function apply parallel `transform` for each transformer in the pipe concatenating
        the results.

        As far as the input for each transformer is the same dataset after the tranformations
        the return columns are renamed like: `<original_col_name>_<transformer_name>`.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return x_new: the new transformed x
        """
        self.logging('transforming x...')
        return self._transform(x)

    @memory
    @timeit
    def transform_y(self, y):
        """Transform `y`.

        This function apply parallel `transform` for each transformer in the pipe concatenating
        the results.

        As far as the input for each transformer is the same dataset after the tranformations
        the return columns are renamed like: `<original_col_name>_<transformer_name>`.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_new: the new transformed y
        """
        self.logging('transforming y...')
        return self._transform(y, proc_x=False)

    @memory
    @timeit
    def inverse_transform_x(self, x):
        """Inverse transform `x`.

        As far this applies transformers in parallel is good enough to invert just one of them
        to get back to the original inputs.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return x_org: the original inverse transformed x
        """
        self.logging('inverse transforming x...')
        x_org = None
        for t in reversed(self.transformers):
            self.logging('-> {}'.format(t.name))
            x_r = t.inverse_transform_x(x)
            if x_r is not None:
                x_org = x_r.copy()
            if x_org is not None:
                break
        assert x_org is not None, 'has been impossible to inverse_transform x'
        self.logging('original x columns: {}'.format(self._original_column_names['x']), level=logging.DEBUG)
        self.logging('inverted x columns: {}'.format(x_org.columns), level=logging.DEBUG)
        assert len(x_org.columns) == len(
            self._original_column_names['x']), 'mismatch number of cols {} expected {}'.format(len(x_org.columns), len(
            self._original_column_names['x']))
        return x_org

    @memory
    @timeit
    def inverse_transform_y(self, y):
        """Inverse transform `y`.

        As far this applies transformers in parallel is good enough to invert just one of them
        to get back to the original inputs.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_org: the original inverse transformed y
        """
        self.logging('inverse transforming y...')
        y_org = None
        for t in reversed(self.transformers):
            self.logging('-> {}'.format(t.name))
            y_r = t.inverse_transform_y(y)
            if y_r is not None:
                y_org = y_r.copy()
            if y_org is not None:
                break
        assert y_org is not None, 'has been impossible to inverse_transform y'
        self.logging('original y columns: {}'.format(self._original_column_names['y']), level=logging.DEBUG)
        self.logging('inverted y columns: {}'.format(y_org.columns), level=logging.DEBUG)
        assert len(y_org.columns) == len(
            self._original_column_names['y']), 'mismatch number of cols {} expected {}'.format(len(y_org.columns), len(
            self._original_column_names['y']))
        return y_org
