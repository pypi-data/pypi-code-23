# -*- coding: utf-8 -*-

from pipesnake.base import Pipe
from pipesnake.base import Transformer
from pipesnake.utils.decorator import memory
from pipesnake.utils.decorator import timeit

__all__ = [
    'SeriesPipe',
]


class SeriesPipe(Pipe, Transformer):
    """:class:`SeriesPipe` applies a list of transformers as series.

    The class itself inherits from :class:`Pipe` and :class:`Transformer` so that it is possible
    to use this as :class:`Transformer` objects.

    Args:
        :param transformers: a list of :class:`Transformer` objects
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline
        :param name: name for this :class:`Transformer`
    """

    def __init__(self, transformers=[], sklearn_output=False, name=None):
        Pipe.__init__(self, transformers=transformers)
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)

    @memory
    @timeit
    def fit_x(self, x):
        """Fit all transformers parameters in the pipe on `x`.

        This function apply sequentially `fit` for each transformer in the pipe.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return self:

        As far as the `fit` of subsequent transformers may be affected by the previous one
        is necessary to execute `fit_transform` here.

        .. todo:: Add some cache system in order to do not recompute this stuff in `transform`.
        """
        self.logging('fitting x...')
        x_new = x.copy()
        for t in self.transformers:
            self.logging('-> {}'.format(t.name))
            x_new = t.fit_transform_x(x_new)
        return self

    @memory
    @timeit
    def fit_y(self, y):
        """Fit all transformers parameters in the pipe on `y`.

        This function apply sequentially `fit` for each transformer in the pipe.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return self:

        As far as the `fit` of subsequent transformers may be affected by the previous one
        is necessary to execute `fit_transform` here.

        .. todo:: Add some cache system in order to do not recompute this stuff in `transform`.
        """
        self.logging('fitting y...')
        y_new = y.copy()
        for t in self.transformers:
            self.logging('-> {}'.format(t.name))
            y_new = t.fit_transform_y(y_new)
        return self

    @memory
    @timeit
    def transform_x(self, x):
        """Transform `x`.

        This function apply sequentially `transform` for each transformer in the pipe.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return x_new: the new transformed x
        """
        self.logging('transforming x...')
        x_new = x.copy()
        for t in self.transformers:
            self.logging('-> {}'.format(t.name))
            x_new = t.transform_x(x_new)
        return x_new

    @memory
    @timeit
    def transform_y(self, y):
        """Transform `y`.

        This function apply sequentially `transform` for each transformer in the pipe.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_new: the new transformed y
        """
        self.logging('transforming y...')
        y_new = y.copy()
        for t in self.transformers:
            self.logging('-> {}'.format(t.name))
            y_new = t.transform_y(y_new)
        return y_new

    @memory
    @timeit
    def inverse_transform_x(self, x):
        """Inverse transform `x`.

        This function apply `inverse_transform` for each transformer in the pipe to get back to the original x and y.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return x_new: the new inverse transformed x
        """
        self.logging('inverse transforming x...')
        x_new = x.copy()
        for t in reversed(self.transformers):
            self.logging('-> {}'.format(t.name))
            x_new = t.inverse_transform_x(x_new)
        return x_new

    @memory
    @timeit
    def inverse_transform_y(self, y):
        """Inverse transform `y`.

        This function apply `inverse_transform` for each transformer in the pipe to get back to the original x and y.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_new: the new inverse transformed y
        """
        self.logging('inverse transforming y...')
        y_new = y.copy()
        for t in reversed(self.transformers):
            self.logging('-> {}'.format(t.name))
            y_new = t.inverse_transform_y(y_new)
        return y_new
