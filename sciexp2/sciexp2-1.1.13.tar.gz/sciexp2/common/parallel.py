#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple parallelization primitives.

By default, the amount of parallelism is controlled by the `PARALLELISM`
variable, interpreted according to `get_parallelism`.

"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2013-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import collections
import contextlib
import multiprocessing
import multiprocessing.pool


#: Default amount of parallelism.
PARALLELISM = True


def get_parallelism(parallelism):
    """Compute the amount of available parallelism according to the system.

    Parameters
    ----------
    parallelism
        Requested parallelism.

    Notes
    -----
    The returned amount of parallelism depends on the value of `parallelism`:

    ================  ======================================================
    Value             Meaning
    ================  ======================================================
    `None`            Use `PARALLELISM` instead.
    `True`            Auto-detect as the number of cores in the system.
    positive integer  Use the given fixed amount.
    negative integer  Auto-detect as the number of cores in the system minus
                      the given value.
    ================  ======================================================

    """
    if parallelism is None:
        parallelism = PARALLELISM

    if parallelism is True:
        parallelism = multiprocessing.cpu_count()
    elif isinstance(parallelism, int):
        if parallelism == 0:
            raise ValueError("Invalid parallelism setting: %s" % parallelism)
        if parallelism < 0:
            parallelism = multiprocessing.cpu_count() + parallelism
    else:
        raise TypeError("Invalid parallelism setting: %s" % parallelism)

    return parallelism


#: Default amount of blocking.
BLOCKING = 50

#: Amount of blocking to use when the work length is unknown.
BLOCKING_UNKNOWN = 20

#: Maximum amount of blocking.
BLOCKING_MAX = 100


def get_blocking(blocking, work_len, parallelism=None):
    """Compute the amount of necessary blocking according to work length.

    Blocking establishes the amount of work items that each worker receives at
    a time. When using processes, this will reduce the costs of communication.

    Parameters
    ----------
    blocking
        Amount of blocking.
    work_len : int or None
        Work length (unknown if `None`).
    parallelism
        Argument to `get_parallelism`.

    Notes
    -----
    Argument `blocking` can mean different things depending on its value type:

    ================  ======================================================
    Value             Meaning
    ================  ======================================================
    `None`            Use `BLOCKING` instead.
    `True`            Evenly partition block with the amount of parallelism.
    positive integer  Use the given fixed amount.
    positive float    Use the given ratio of the given work elements, up to
                      `BLOCKING_MAX`.
    ================  ======================================================

    If the work size is unknown, `True` or a float argument will revert to
    `BLOCKING_UNKNOWN`.

    """
    if blocking is None:
        blocking = BLOCKING
    if blocking is True:
        if work_len is None:
            blocking = BLOCKING_UNKNOWN
        else:
            parallelism = get_parallelism(parallelism)
            blocking = work_len / parallelism
    elif isinstance(blocking, float):
        if work_len is None:
            blocking = BLOCKING_UNKNOWN
        else:
            blocking = min(work_len * blocking, BLOCKING_MAX)
    elif not isinstance(blocking, int):
        raise TypeError("Invalid blocking setting: %s" % blocking)
    return blocking


@contextlib.contextmanager
def configuration(**kwargs):
    """Context manager to temporarily override global parameters.

    Parameters
    ----------
    kwargs
        Temporary values to global parameters.

    Examples
    --------
    Temporarily override the default parallelism to all cores minus one and set
    blocking to 100:

    >>> def fadd (x) : return x + 1
    >>> def fmul (x) : return x * 2
    >>> with configuration(PARALLELISM = -1, BLOCKING = 100):
    ...    s = p_imap(range(10000), fadd)
    ...    res = p_imap(s, fmul)                       # doctest: +SKIP

    This is equivalent to:
    >>> s = p_imap(range(10000), fadd,
    ...            parallelism = -1, blocking = 100)   # doctest: +SKIP
    >>> res = p_imap(s, fmul,
    ...              parallelism = -1, blocking = 100) # doctest: +SKIP

    """
    variables = ["PARALLELISM", "BLOCKING", "BLOCKING_UNKNOWN", "BLOCKING_MAX"]
    backup = {}
    new = {}
    for var in variables:
        backup[var] = globals()[var]
        new[var] = kwargs.pop(var, backup[var])

    if len(kwargs) > 0:
        raise KeyError("Unknown globals: %s" % ", ".join(kwargs.keys()))

    globals().update(new)

    yield None

    globals().update(backup)


def _p_init(work, parallelism, blocking):
    if isinstance(work, collections.Sized):
        work_len = len(work)
    else:
        work_len = None

    parallelism = get_parallelism(parallelism)
    blocking = get_blocking(blocking, work_len, parallelism)
    pool = multiprocessing.Pool(processes=parallelism)
    return pool, blocking


def p_imap(work, func, parallelism=None, blocking=None):
    """Return a sequence with the result of mapping `func` to `work` in parallel.

    This function uses processes.

    Parameters
    ----------
    work : sequence
        Sequence of items to process in parallel.
    func : callable
        Function to apply on each element of `work`.
    parallelism
        Argument to `get_parallelism`.
    blocking
        Argument to `get_blocking`.

    See also
    --------
    multiprocessing.Pool, multiprocessing.Pool.imap

    """
    pool, blocking = _p_init(work, parallelism, blocking)
    res = iter(pool.imap(func, work, chunksize=blocking))
    pool.close()
    return res


def p_imap_unordered(work, func, parallelism=None, blocking=None):
    """Return a sequence with the result of mapping `func` to `work` in parallel.

    This function uses processes.

    Parameters
    ----------
    work : sequence
        Sequence of items to process in parallel.
    func : callable
        Function to apply on each element of `work`.
    parallelism
        Argument to `get_parallelism`.
    blocking
        Argument to `get_blocking`.

    See also
    --------
    multiprocessing.Pool, multiprocessing.Pool.imap_unordered

    """
    pool, blocking = _p_init(work, parallelism, blocking)
    res = iter(pool.imap_unordered(func, work, chunksize=blocking))
    pool.close()
    return res


def p_map(work, func, parallelism=None, blocking=None):
    """Return a list with the result of mapping `func` to `work` in parallel.

    This function uses processes.

    Parameters
    ----------
    work : sequence
        Sequence of items to process in parallel.
    func : callable
        Function to apply on each element of `work`.
    parallelism
        Argument to `get_parallelism`.
    blocking
        Argument to `get_blocking`.

    See also
    --------
    multiprocessing.Pool, multiprocessing.Pool.map

    """
    pool, blocking = _p_init(work, parallelism, blocking)
    res = pool.map(func, work, chunksize=blocking)
    pool.close()
    return res


def _t_init(work, parallelism, blocking):
    if isinstance(work, collections.Sized):
        work_len = len(work)
    else:
        work_len = None

    parallelism = get_parallelism(parallelism)
    blocking = get_blocking(blocking, work_len, parallelism)
    pool = multiprocessing.pool.ThreadPool(processes=parallelism)
    return pool, blocking


def t_imap(work, func, parallelism=None, blocking=None):
    """Return a sequence with the result of mapping `func` to `work` in parallel.

    This function uses threads.

    Parameters
    ----------
    work : sequence
        Sequence of items to process in parallel.
    func : callable
        Function to apply on each element of `work`.
    parallelism
        Argument to `get_parallelism`.
    blocking
        Argument to `get_blocking`.

    See also
    --------
    multiprocessing.pool.ThreadPool, multiprocessing.pool.ThreadPool.imap

    """
    pool, blocking = _t_init(work, parallelism, blocking)
    res = iter(pool.imap(func, work, chunksize=blocking))
    pool.close()
    return res


def t_imap_unordered(work, func, parallelism=None, blocking=None):
    """Return a sequence with the result of mapping `func` to `work` in parallel.

    This function uses threads.

    Parameters
    ----------
    work : sequence
        Sequence of items to process in parallel.
    func : callable
        Function to apply on each element of `work`.
    parallelism
        Argument to `get_parallelism`.
    blocking
        Argument to `get_blocking`.

    See also
    --------
    multiprocessing.pool.ThreadPool, multiprocessing.pool.ThreadPool.imap

    """
    pool, blocking = _t_init(work, parallelism, blocking)
    res = iter(pool.imap_unordered(func, work, chunksize=blocking))
    pool.close()
    return res


def t_map(work, func, parallelism=None, blocking=None):
    """Return a list with the result of mapping `func` to `work` in parallel.

    This function uses threads.

    Parameters
    ----------
    work : sequence
        Sequence of items to process in parallel.
    func : callable
        Function to apply on each element of `work`.
    parallelism
        Argument to `get_parallelism`.
    blocking
        Argument to `get_blocking`.

    See also
    --------
    multiprocessing.pool.ThreadPool, multiprocessing.pool.ThreadPool.map

    """
    pool, blocking = _t_init(work, parallelism, blocking)
    res = pool.map(func, work, chunksize=blocking)
    pool.close()
    return res
