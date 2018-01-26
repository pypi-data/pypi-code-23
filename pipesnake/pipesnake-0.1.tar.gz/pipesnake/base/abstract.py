# -*- coding: utf-8 -*-

import logging
from abc import ABCMeta
from abc import abstractmethod
from copy import deepcopy
from random import getrandbits

from sklearn.base import BaseEstimator

from pipesnake.base.utils import _check_input
from pipesnake.base.utils import _check_transformer_type
from pipesnake.utils import to_snake

__all__ = [
    'Transformer',
    'Pipe',
]


class Transformer(BaseEstimator):
    """Transformer abstract class freely inspired by Scikit-Learn.

     See `TransformerMixin <https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/base.py>`_
     for more details, the main differences are the parameters type and the returns.
     Note: that this inherits from sklearn BaseEstimator to simplify the parameters managment.
     """
    __metaclass__ = ABCMeta

    def __init__(self, name=None, sklearn_output=False, **kwargs):
        """
        :param name: provide a name for this transfomer
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline
        """
        self.name = name
        if name is None:
            # if no name is provided name will be assigned as the class name with a random hex
            self.name = to_snake(self.__class__.__name__) + '_{:02x}'.format(getrandbits(16))
        self.sklearn_output = sklearn_output

    @abstractmethod
    def fit_x(self, x):
        """Fit the Transformer parameters for `x`.

        This function is intended for implementing the
        computation of the parameters needed for transform function.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return self:
        Raises:
            `NotImplementedError`: function not implemented
        """
        raise NotImplementedError()

    @abstractmethod
    def fit_y(self, y):
        """Fit the Transformer parameters for `y`.

        This function is intended for implementing the
        computation of the parameters needed for transform function.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return self:
        Raises:
            `NotImplementedError`: function not implemented
        """
        raise NotImplementedError()

    def fit(self, x, y=None):
        """Fit the Transformer parameters.

        If `x` or `y` are not Pandas DataFrame not fit will be performed

        Note: `y=None` as default is to be compliant with scikit-learn

        Returns:
            :return self:
        """
        self.logging('fitting...', level=logging.DEBUG)
        if _check_input(x, self.logging):
            self.fit_x(x)
        if _check_input(y, self.logging):
            self.fit_y(y)
        return self

    @abstractmethod
    def transform_x(self, x):
        """Transform `x`.

        This function is intended to implement the actual transformation on
        x.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return x_new: the new transformed x
        Raises:
            `NotImplementedError`: function not implemented
        """
        raise NotImplementedError()

    @abstractmethod
    def transform_y(self, y):
        """Transform `y`.

        This function is intended to implement the actual transformation on
        y.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_new: the new transformed y
        Raises:
            `NotImplementedError`: function not implemented
        """
        raise NotImplementedError()

    def transform(self, x, y=None):
        """Transform `x` and `y`.

        If `x` or `y` are not Pandas DataFrame the original value will be returned

        Note: `y=None` as default is to be compliant with scikit-learn

        Returns:
            :return x_new: the new transformed x
            :return y_new: the new transformed y

        .. todo:: This can be parallelized in computation on x and y
        """
        self.logging('transforming...', level=logging.DEBUG)
        _x = x
        if _check_input(x, self.logging):
            _x = self.transform_x(x)
        if self.sklearn_output:
            return _x
        _y = y
        if _check_input(y, self.logging):
            _y = self.transform_y(y)
        return _x, _y

    def fit_transform(self, x, y=None):
        """Apply `fit` and `transform` functions.

        Note: `y=None` as default is to be compliant with scikit-learn

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return x_new: the new transformed x
            :return y_new: the new transformed y
        """
        return self.fit(x, y).transform(x, y)

    def fit_transform_x(self, x):
        """Apply `fit` and `transform` functions only on `x`.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return x_new: the new transformed x
        """
        return self.fit_x(x).transform_x(x)

    def fit_transform_y(self, y):
        """Apply `fit` and `transform` functions only on `y`.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_new: the new transformed y
        """
        return self.fit_y(y).transform_y(y)

    @abstractmethod
    def inverse_transform_x(self, x):
        """Inverse transform `x`.

        This function is intended to implement the inverse
        transform to get back to the original x.

        Args:
            :param x: a Pandas Dataframe of shape [n_samples, n_features] the dataset
        Returns:
            :return x_org: the original inverse transformed x
        Raises:
            `NotImplementedError`: function not implemented
        """
        raise NotImplementedError()

    @abstractmethod
    def inverse_transform_y(self, y):
        """Inverse transform `y`.

        This function is intended to implement the inverse
        transform to get back to the original y.

        Args:
            :param y: a Pandas Dataframe of shape [n_samples] the target
        Returns:
            :return y_org: the original inverse transformed y
        Raises:
            `NotImplementedError`: function not implemented
        """
        raise NotImplementedError()

    def inverse_transform(self, x, y=None):
        """Inverse transform `x` and `y`.

        This function is intended to implement the inverse
        transform to get back to the original x and y.

        Note: `y=None` as default is to be compliant with scikit-learn

        Returns:
            :return x_org: the new inverse transformed x
            :return y_org: the new inverse transformed y
        """
        self.logging('inverse transforming...', level=logging.DEBUG)
        _x = x
        if _check_input(x, self.logging):
            _x = self.inverse_transform_x(x)
        if self.sklearn_output:
            return _x
        _y = y
        if _check_input(y, self.logging):
            _y = self.inverse_transform_y(y)
        return _x, _y

    def logging(self, msg, level=logging.INFO):
        """Helper function to log info related to Transformer

        Args:
            :param msg: the message to log
            :param level: logging level enum (https://docs.python.org/2/library/logging.html#logging-levels)
        """
        logging.log(level, '[{}] : {}'.format(self.name, msg))


class Pipe(object):
    """Pipe abstract class to apply a list of transformers.

    This provides all basic wiring to deal with list of transformers.

    :param name: a name for this pipe object
    :param transformers: a list of transfomers
    """

    def __init__(self, transformers=[]):
        self.transformers = transformers

    def __len__(self):
        return len(self.transformers)

    def __iter__(self):
        return iter(self.transformers)

    def __str__(self):
        s = '['
        for c in self.transformers:
            s += str(c) + ', '
        return s[:-1] + ']'

    def __getitem__(self, index):
        return self.transformers[index]

    def __setitem__(self, index, transformer):
        assert _check_transformer_type(transformer, self.logging), 'Mismatched type: expected Transformer got {0}'.format(
            type(transformer))
        self.transformers[index] = transformer

    def __delitem__(self, index):
        del self.transformers[index]

    def copy(self, transformers):
        """Copy a list of :class:`Transformer` objects to this object."""
        del self.transformers[:]
        for t in transformers:
            self.transformers.append(t)

    def clone(self):
        """Clone this object."""
        return deepcopy(self)

    def append(self, transformer):
        assert _check_transformer_type(transformer, self.logging), 'Mismatched type: expected Transformer got {0}'.format(
            type(transformer))
        self.transformers.append(transformer)

    def extend(self, transformers):
        for t in transformers:
            self.append(t)
