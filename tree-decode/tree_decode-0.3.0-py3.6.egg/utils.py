"""
Useful utilities for our tree-decoding API.
"""

from sklearn.utils.validation import check_is_fitted as _check_is_fitted
from sklearn.tree.tree import BaseDecisionTree
from sklearn.ensemble.forest import BaseForest
from sklearn.exceptions import NotFittedError


def check_model_type(model):
    """
    Check that the data type of model is one that we support.

    Currently, the estimators we support are:

    * DecisionTreeClassifier
    * DecisionTreeRegressor
    * ExtraTreeClassifier
    * ExtraTreeRegressor

    * RandomForestClassifier
    * RandomForestRegressor
    * ExtraTreesClassifier
    * ExtraTreesRegressor

    Parameters
    ----------
    model : object
        The model to check.

    Raises
    ------
    NotImplementedError : the data type of the model was one that
                          we do not support at the moment.
    """

    if not isinstance(model, (BaseDecisionTree, BaseForest)):
        klass = type(model).__name__
        raise NotImplementedError("Function support is not implemented for "
                                  "{klass}.".format(klass=klass))


def check_is_fitted(model):
    """
    Check whether a model has been fitted.

    This function only applies to tree-based models and is a subset of
    scikit-learn's `check_is_fitted` function.

    Parameters
    ----------
    model : object
        The model to check.

    Returns
    -------
    is_fitted : bool
        Whether or not the model is fitted.

    Raises
    ------
    NotImplementedError : the data type of the model is not supported.
    """

    if isinstance(model, BaseDecisionTree):
        _check_is_fitted(model, "tree_")
    elif isinstance(model, BaseForest):
        _check_is_fitted(model, "estimators_")
    else:
        klass = type(model).__name__
        raise NotImplementedError("Function support is not implemented for "
                                  "{klass}.".format(klass=klass))


def get_estimators(model):
    """
    Get an iterable array of estimators given an ensemble or estimator.

    Parameters
    ----------
    model : sklearn.ensemble.forest.BaseForest or
            sklearn.tree.tree.BaseDecisionTree
        The model whose estimator(s) we are extracting.

    Returns
    -------
    estimator_array : list
        A list of estimators that can be used for processing.

    Raises
    ------
    NotImplementedError : the data type of the model is invalid for extracting
        an estimator(s) from the model.
    """

    if isinstance(model, BaseDecisionTree):
        return [model]
    elif isinstance(model, BaseForest):
        try:
            return model.estimators_
        except AttributeError:
            msg = ("The ensemble model needs to be fitted first "
                   "before estimators can be extracted")
            raise NotFittedError(msg)
    else:
        klass = type(model).__name__
        raise NotImplementedError("Cannot extract estimators for "
                                  "{klass}.".format(klass=klass))


def get_tab(size=5):
    """
    Get a tab composed of a given number of spaces.

    Parameters
    ----------
    size : int, default 5
        The number of spaces to use for a tab.

    Returns
    -------
    tab_str : str
        The provided tab to a given number of spaces.
    """

    return " " * size


def get_tree_at(ensemble, index):
    """
    Extract a single tree from an ensemble model.

    Ensemble models store their trees in an array, which can be indexed like
    a list or any other array-like. This utility allows users to do that
    type of accessing without having to remember the name of the array that
    stores these trees.

    Parameters
    ----------
    ensemble : sklearn.ensemble.forest.BaseForest
        The ensemble model from which to extract a tree. This function expects
        that the ensemble is already fitted.
    index : int
        The index of the intended tree. To avoid an `IndexError`, it should be
        in the range of [0, number_of_trees - 1].

    Returns
    -------
    tree : sklearn.tree.tree.BaseDecisionTree
        The extracted tree from the ensemble.

    Raises
    ------
    IndexError : An invalid index was passed in to retrieve a tree.
    NotFittedError : The model has not been fitted yet, so obtaining
        an estimator is invalid in this case.
    TypeError : The object passed in was not a valid ensemble model.
    """

    if not isinstance(ensemble, BaseForest):
        raise TypeError("This is not a valid tree ensemble model")

    try:
        return ensemble.estimators_[index]
    except AttributeError:
        msg = "This model has not been fitted yet"
        raise NotFittedError(msg)
    except IndexError:
        msg = "There is no tree at index {i}"
        raise IndexError(msg.format(i=index))


def maybe_round(val, precision=None):
    """
    Potentially round a number or an array of numbers to a given precision.

    Parameters
    ----------
    val : numeric or numpy.ndarray
        The number or array of numbers to round.
    precision : int, default None
        The precision at which to perform rounding. If None is provided,

    Returns
    -------
    maybe_rounded_val : the number or array of numbers rounded to a
                        given precision, if provided. Otherwise, the
                        original input is returned.
    """

    if precision is None:
        return val

    if hasattr(val, "round"):
        return val.round(precision)
    else:
        return round(val, precision)


def write_to_buf(output, filepath_or_buffer=None):
    """
    Write output to a file or buffer. If none is provided, nothing happens.

    Parameters
    ----------
    output : str
        The output to write.
    filepath_or_buffer : str or file handle, default None
        The file or buffer to which to write the output.
    """

    if filepath_or_buffer is None:
        return

    # We want to preserve state when writing to a buffer.
    # If a buffer was provided, we don't close it. If a
    # path is provided, we close the file buffer once we
    # finish writing to the given filepath.
    if isinstance(filepath_or_buffer, str):
        f = open(filepath_or_buffer, "w")
        close_file = True
    else:
        f = filepath_or_buffer
        close_file = False

    try:
        f.write(output)
    finally:
        if close_file:
            f.close()
