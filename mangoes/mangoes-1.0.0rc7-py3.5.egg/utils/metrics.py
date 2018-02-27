# -*- coding: utf-8 -*-
"""Utility metrics functions.

"""

import logging

import numpy as np
import sklearn.metrics

import mangoes.utils.arrays

logger = logging.getLogger(__name__)


def rowwise_cosine_similarity(A, B):
    """Compute cosine_similarity between each corresponding rows of A and B

    Parameters
    ----------
    A: matrix-like object
    B: matrix-like object

    Returns
    -------
    list of float
    """
    if len(A.shape) == 1:
        return sklearn.metrics.pairwise.cosine_similarity(A.reshape((1, -1)), B.reshape((1, -1)))

    # TODO : unify sparse and non sparse
    import scipy.sparse
    if scipy.sparse.issparse(A):
        return np.array(
            [sklearn.metrics.pairwise.cosine_similarity(a.toarray().reshape((1, -1)),
                                                        b.toarray().reshape((1, -1)))[0][0]
             for (a, b) in zip(A, B)])

    return np.array(
        [sklearn.metrics.pairwise.cosine_similarity(a.reshape((1, -1)), b.reshape((1, -1)))[0][0]
         for (a, b) in zip(A, B)])


def pairwise_non_negative_cosine_similarity(first, second, normalize=True):
    """Compute non negative cosine similary between all pairs of vectors in matrices

    Parameters
    ----------
    first: matrix-like object
        :class:`mangoes.utils.arrays.Matrix` with n vectors
    second: matrix-like object
        :class:`mangoes.utils.arrays.Matrix` with k vectors
    normalize: bool
        the matrices have to be normalized : if they both are, set this parameter to False

    Returns
    -------
    matrix-like object
        :class:`mangoes.utils.arrays.Matrix` of shape (n x k)
    """
    if normalize:
        first, second = first.normalize(), second.normalize()

    similarities = first.dot(second.T)  # TODO : check if already normalized
    try:
        return mangoes.utils.arrays.Matrix.factory((similarities + 1) / 2)
    except NotImplementedError:
        # adding a nonzero scalar to a sparse matrix is not yet supported
        return mangoes.utils.arrays.Matrix.factory((similarities.todense() + 1) / 2)


def pairwise_cosine_similarity(first, second, normalize=True):
    """Compute cosine similary between all pairs of vectors in matrices

    Parameters
    ----------
    first: matrix-like object
        a mangoes.utils.arrays.Matrix with n vectors
    second: matrix-like object
        a mangoes.utils.arrays.Matrix with k vectors
    normalize: bool
        the matrices have to be normalized : if they both are, set this parameter to False

    Returns
    -------
    matrix-like object
        mangoes.utils.arrays.Matrix of shape (n x k)
    """
    if normalize:
        first, second = first.normalize(), second.normalize()

    similarities = first.dot(second.T)  # TODO : check if already normalized

    import scipy.sparse  # TODO : try/except
    if scipy.sparse.issparse(similarities):
        similarities = similarities.todense()
    return np.array(similarities)
