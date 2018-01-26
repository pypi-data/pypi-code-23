# -*- coding: utf-8 -*-

import logging

import pandas
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import KNeighborsRegressor

from pipesnake.base import Transformer
from pipesnake.base.utils import _check_cols
from pipesnake.base.utils import _is_categorical_cols
from pipesnake.base.utils import _shape
from pipesnake.transformers.converter import Category2Number

__all__ = [
    'ReplaceImputer',
    'KnnImputer',
]


class ReplaceImputer(Transformer):
    """Impute NaNs replacing them.

    Replace NaNs using different strategies. Note that categorical columns will not be imputed see :class:`Category2Number`

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param value: the value to be used in the imputation, it can be a number or `'mean'` or `'median'`, in the last
                      two cases the value is the mean or the median of the given column
        :param method:  {`backfill`, `bfill`, `pad`, `ffill`, `None`}, (default: `None`). Method to use for filling holes
                         in reindexed Series pad / ffill: propagate last valid observation forward to next valid
                         backfill / bfill: use NEXT valid observation to fill gap. More details: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.fillna.html
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> imputer = ReplaceImputer()
    >>> x_new, y_new = imputer.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], value='median', method=None, sklearn_output=False, name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.value = value
        self.method = method

    def fit_x(self, x):
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        return self

    def fit_y(self, y):
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        return self

    def _transform(self, data, cols):
        if len(cols) == 0:
            return data
        _data = data.copy()
        value = {c: self.value for c in cols}
        if type(self.value) == str:
            if self.value == 'mean':
                value = _data[cols].mean().to_dict()
            if self.value == 'median':
                value = _data[cols].median().to_dict()
        _data.fillna(value=value, method=self.method, inplace=True)
        return _data

    def transform_x(self, x):
        return self._transform(x, self.x_cols)

    def transform_y(self, y):
        return self._transform(y, self.y_cols)

    def inverse_transform_x(self, x):
        self.logging('removing nan values in x is not invertible as transformation', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('removing nan values in y is not invertible as transformation', level=logging.WARNING)
        return y


class KnnImputer(Transformer):
    """Impute NaNs using K-nearest neighbors.

    Replace NaNs using different Knn approach

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param k: k value for Knn algorithm
        :param x_is_categorical: a list of boolean indicating categorical columns, if `None` categorical will be autodetect
                                 using the type of the column, all non numerical columns will be treated as categorical (default: `None`)
        :param y_is_categorical: a list of boolean indicating categorical columns, if `None` categorical will be autodetect
                                 using the type of the column, all non numerical columns will be treated as categorical (default: `None`)
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> imputer = KnnImputer()
    >>> x_new, y_new = imputer.fit_transform(x, y)
    """

    def __init__(self, x_cols=[], y_cols=[], k=3, x_is_categorical=None, y_is_categorical=None, sklearn_output=False,
                 name=None):
        Transformer.__init__(self, sklearn_output=sklearn_output, name=name)
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.k = k
        self.x_is_categorical = x_is_categorical
        self.y_is_categorical = y_is_categorical
        self._cat2num = {'x': None, 'y': None}  # this is needed to deal with potential categorical columns
        self._knn_models = {'x': None, 'y': None}

    def _fit(self, data, cols, is_categorical, cat2num):
        if len(cols) == 0:
            return data
        assert _shape(data)[1] >= 2, 'at least 2 columns are needed'
        _data = data.copy()

        nan_ids = pandas.isnull(data).any(axis=1).nonzero()[0].tolist()
        _data.drop(nan_ids, inplace=True)
        self.logging('current shape: {}'.format(_shape(_data)))
        assert _shape(_data)[0] >= self.k, 'not enough rows: {} removed {} rows'.format(_shape(_data)[0], len(nan_ids))

        _data, _ = cat2num.fit_transform(_data, None)

        models = {}
        for col, cat in zip(cols, is_categorical):
            if cat:
                models[col] = KNeighborsClassifier(n_neighbors=self.k)
            else:
                models[col] = KNeighborsRegressor(n_neighbors=self.k)
            x_train = _data[list(set(_data.columns.tolist()) - set([col]))]
            y_train = _data[col]
            self.logging(
                'fitting imputing_model for column: {} x_train.shape={} y_train.shape={}'.format(col, _shape(x_train),
                                                                                                 _shape(y_train)),
                                                                                                 level=logging.DEBUG)
            models[col].fit(x_train, y_train)
        return models

    def fit_x(self, x):
        self.x_cols = _check_cols(x, self.x_cols, self.logging)
        self.logging('x_cols: {}'.format(self.x_cols), level=logging.DEBUG)
        if not self.x_is_categorical or len(self.x_is_categorical) != len(self.x_cols):
            self.x_is_categorical = _is_categorical_cols(x, self.x_cols)
        categorical_cols = [self.x_cols[i] for i, v in enumerate(self.x_is_categorical) if v]
        self._cat2num['x'] = Category2Number(x_cols=categorical_cols, skipna=True)
        self._knn_models['x'] = self._fit(x, self.x_cols, self.x_is_categorical, self._cat2num['x'])
        return self

    def fit_y(self, y):
        self.y_cols = _check_cols(y, self.y_cols, self.logging)
        self.logging('y_cols: {}'.format(self.y_cols), level=logging.DEBUG)
        if not self.y_is_categorical or len(self.y_is_categorical) != len(self.y_cols):
            self.y_is_categorical = _is_categorical_cols(y, self.y_cols)
        categorical_cols = [self.y_cols[i] for i, v in enumerate(self.y_is_categorical) if v]
        self._cat2num['y'] = Category2Number(x_cols=categorical_cols, skipna=True)  # yes, it is x_col
        self._knn_models['y'] = self._fit(y, self.y_cols, self.y_is_categorical, self._cat2num['y'])
        return self

    def _transform(self, data, cols, cat2num, models):
        if len(cols) == 0:
            return data
        _data = data.copy()
        _data, _ = cat2num.transform(_data, None)

        # compute imputation values
        impute_values = {}
        for col in _data.columns.values.tolist():
            impute_values[col] = _data[col].mode().iloc[0]

        for col in cols:
            nan_ids = pandas.isnull(_data[col]).nonzero()[0].tolist()
            if len(nan_ids) == 0:
                continue
            x_pred = _data.loc[nan_ids].copy()
            x_pred.drop([col], axis=1, inplace=True)
            x_pred.fillna(value=impute_values, inplace=True)  # temporary imputation for other missing values
            self.logging('predicting model for column: {}'.format(col), level=logging.DEBUG)
            _data.loc[nan_ids, col] = models[col].predict(x_pred)

        _data, _ = cat2num.inverse_transform(_data, None)
        return _data

    def transform_x(self, x):
        return self._transform(x, self.x_cols, self._cat2num['x'], self._knn_models['x'])

    def transform_y(self, y):
        return self._transform(y, self.y_cols, self._cat2num['y'], self._knn_models['y'])

    def inverse_transform_x(self, x):
        self.logging('removing nan cols in x is not invertible as transformation', level=logging.WARNING)
        return x

    def inverse_transform_y(self, y):
        self.logging('removing nan cols y is not invertible as transformation', level=logging.WARNING)
        return y
