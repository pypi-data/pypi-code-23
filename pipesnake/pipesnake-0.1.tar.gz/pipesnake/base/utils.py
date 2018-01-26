# -*- coding: utf-8 -*-

import logging

import pandas


def _check_transformer_type(obj, logger):
    """ Check if a given object is :class:`Transformer`

    :param obj: the instance
    :return: True if it is :class:`Transformer` False otherwise
    """
    if not (hasattr(obj, 'fit') and callable(obj.fit)):
        logger('{} seems not be a Transformer'.format(type(obj)), level=logging.WARNING)
        return False
    if not (hasattr(obj, 'transform') and callable(obj.transform)):
        logger('{} seems not be a Transformer'.format(type(obj)), level=logging.WARNING)
        return False
    if not (hasattr(obj, 'fit_transform') and callable(obj.fit_transform)):
        logger('{} seems not be a Transformer'.format(type(obj)), level=logging.WARNING)
        return False
    if not (hasattr(obj, 'inverse_transform') and callable(obj.inverse_transform)):
        logger('{} seems not be a Transformer'.format(type(obj)), level=logging.WARNING)
        return False
    return True


def _check_input(df, logger):
    """Check input type and number or rows

    Args:
        :param df: a pandas DataFrame
    Return:
        :return: True if everything is ok
    """
    if '.DataFrame' in str(type(df)):
        if len(df) > 0:
            return True
        else:
            logger('input has not enough rows, got shape {}'.format(df.shape), level=logging.WARNING)
            return False
    else:
        logger('input is not a Pandas DataFrame, instead got {}'.format(type(df)), level=logging.WARNING)
        return False


def _check_cols(df, cols, logger):
    """Produce a correct list of columns for this DataFrame

    Args:
        :param df: a pandas DataFrame
        :param cols: a list of column names or a list of indices; 'all' to use all columns; if [] no columns will be affected
    Return:
        :return: a convalidated list of columns for this DataFrame
    Raise:
        :exception: unknown type of columns
    """

    if type(cols) == str and cols == 'all':
        return df.columns.values.tolist()
    elif type(cols) == list:
        _cols = []
        for c in cols:
            if type(c) == int:
                _cols.append(df.columns.values[c])
            else:
                _cols.append(c)
        return _cols
    else:
        logger('unknown type of columns: {} ({})'.format(type(cols), cols), level=logging.WARNING)
        raise Exception('unknown type of columns: {} ({})'.format(type(cols), cols))


def _is_categorical_cols(df, cols):
    """Detect if column type is a number or string

    Args:
        :param df: a pandas DataFrame
        :param cols: a list of column names
    Return:
        :return: a boolean list of same lenght as cols with True in position where the column is not numerical
    Raise:
        :exception: unknown type of columns
    """
    is_categorical = []
    for c in cols:
        is_categorical.append(not pandas.np.issubdtype(df[c].dtype, pandas.np.number))
    return is_categorical


def _shape(df):
    """ Return DataFrame shape even if is not a Pandas dataframe."""
    if type(df) == pandas.DataFrame or type(df) == pandas.Series:
        return df.shape
    try:
        shape = (len(df), len(df.columns))
    except Exception as e:
        logging.error(e)
        raise e
    return shape
