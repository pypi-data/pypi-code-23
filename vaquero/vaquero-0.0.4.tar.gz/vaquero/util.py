from __future__ import print_function

import os
import json
import numpy as np
import pandas as pd
from contextlib import contextmanager
from fnmatch import fnmatch
from functools import partial, reduce
from collections import OrderedDict
from itertools import islice as take


def first(items):
    """
    Get the first item from an iterable.

    Warning: It consumes from a generator.

    :param items: an iterable
    :return: the first in the iterable
    """
    for item in items:
        return item


def nth(items, i):
    """
    Get the nth item from an iterable.

    Warning: It consumes from a generator.

    :param items: an iterable
    :return: the first in the iterable
    """
    for j, item in enumerate(items):
        if j == i:
            return item


def tap(items, f=print):
    """
    Apply f (default=print) to each item in items then yield the item.


    :param items: an iterable
    :param f: function to call for each item in items

    """
    for item in items:
        f(item)
        yield item


def find(items, predicate):
    """
    Find the item in an iterable.

    :param items: an iterable
    :param predicate: a function which returns true if it matches your query
    :return: the first item which matched the predicate, else None
    """
    for item in items:
        if predicate(item):
            return item
    return None


def slurp(file_path):
    """
    Open, read, and close a file.

    :param file_path: the file to process
    :return: the result of calling `read`
    """
    with open(file_path) as fp:
        return fp.read()


def jsonlines_reader(file_path, skip_decode_errors=False):
    """
    Yield each document in a JSON-lines document.
    :param file_path: filepath to a json-lines file set
    """
    with open(file_path) as fp:
        for line in fp:
            try:
                yield json.loads(line)
            except ValueError:
                if not skip_decode_errors:
                    raise


def examine_pairwise_result(f, input_doc):
    """
    Test f against input doc and return the resulting dict.

    :param f: a function with a `f(src_obj, dst_dict)` signature
    :param input_doc: the input object
    :return: a dictionary populated via f
    """
    d = OrderedDict()
    f(input_doc, d)
    return d


def files_processor(generator_func, dir_path, shell_ptn="*", recursive=False):
    """
    Process some files as a stream of entities.

    :param generator_func: a function which takes a file path and generates
        items to process (e.g. jsonlines_reader)
    :param dir_path: the root directory to examine
    :param shell_ptn: the shell pattern for matching file names (e.g. jsonl)
    :param recursive: if True, then traverse subdirectories
    """
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if recursive and os.path.isdir(file_path):
            for item in files_processor(generator_func, file_path,
                                        shell_ptn, True):
                yield item
        elif fnmatch(file_name, shell_ptn):
            for item in generator_func(file_path):
                yield item


def jsonl_files_entities(dir_path, file_suffix="jsonl", recursive=False):
    """
    Helper function to process all json-line files in a directory.

    :param dir_path: the directory containing jsonl files
    :param file_suffix: the file suffix to accept
    :param recursive: if True, scan recursively
    """
    ptn = "*." + file_suffix
    for entry in files_processor(jsonlines_reader, dir_path, ptn):
        yield entry


def pd_print_entirely(frame_or_series):
    """
    Print a pandas dataframe or series in its entirety.

    :param frame_or_series: a pandas Series or DataFrame
    """
    columns = pd.get_option('display.max_columns')
    pd.set_option('display.max_columns', None)

    rows = pd.get_option('display.max_rows')
    pd.set_option('display.max_rows', None)

    try:
        print(frame_or_series)
    finally:
        pd.set_option('display.max_columns', columns)
        pd.set_option('display.max_rows', rows)


def np_and(condition, *conditions):
    # This is just much less noise then (a) && (b) && (c) to me.
    return reduce(np.logical_and, conditions, condition)


def np_or(condition, *conditions):
    # This is just much less noise then (a) || (b) || (c) to me.
    return reduce(np.logical_or, conditions, condition)


try:
    from contextlib import suppress
except ImportError:
    @contextmanager
    def suppress(*exceptions):
        try:
            yield
        except exceptions:
            pass


class OpCollector:
    """
    Collects state-changing ops on an underlying object for deferred execution.
    """

    def __init__(self, obj, eager=True, swallow_exceptions=None):
        """
        :param obj: the underlying object for deferred manipulation
        :param eager: if True (default) check for the existence of the
            selected attribute at log time, rather than application time
        :param swallow_exceptions: an list of exceptions to swallow at
            application time
        """
        self._obj = obj
        self._ops = []
        self._eager = eager
        self._swallow_exceptions = swallow_exceptions or []

    @property
    def ops(self):
        return self._ops

    def apply_all(self):
        """
        Apply the deferred operations to the underlying object

        :return: the number of successful applications
        """
        n_successful = 0
        for name, args, kwargs in self._ops:
            with suppress(*self._swallow_exceptions):
                getattr(self._obj, name)(*args, **kwargs)
                n_successful += 1
        self._ops = []
        return n_successful

    def __delitem__(self, *args, **kwargs):
        return self._log_call('__delitem__', *args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._log_call('__call__', *args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self._log_call('__setitem__', *args, **kwargs)

    def _log_call(self, name, *args, **kwargs):
        if self._eager:
            getattr(self._obj, name)  # Raises an attribute error

        i = len(self._ops)
        self._ops.append((name, args, kwargs))
        return i

    def __getattr__(self, name):
        return partial(self._log_call, name)

    def __str__(self):
        msg_fmt = "OpCollector([{} ops ready for processing])"
        return msg_fmt.format(len(self._ops))

    def __repr__(self):
        return self.__str__()


@contextmanager
def deferred_delete(obj, skip_missing=True):
    """
    Context manager for performing deferred deletes on some dictionary.

    Generally useful for identifying which keys to delete in a loop, then
    having them automatically deleted later, since you can't delete
    mid-iteration (a RuntimeError).

    Deletions execute in order. And, multiple calls to delete are possible.


    :param obj: the dictionary (or some object implementing `__delitem__`)
    :param skip_missing: if True then the deferred operation only calls
        the delete if the key is present in the underlying object
    """
    ops = OpCollector(obj,
                      eager=False,
                      swallow_exceptions=[KeyError] if skip_missing else [])
    yield ops
    ops.apply_all()  # Note: Only executes if no exception raised to context


def chunking(items, n):
    """
    Convert sequence of items into sequence of n-sized sequences

    The final sequence always gets yielded, even if less than n.

    :param items: items to chunk
    :param n: number of items per chunk:
    """
    chunk = []
    for item in items:
        if len(chunk) == n:
            yield chunk
            chunk = []

        chunk.append(item)

    if chunk:
        yield chunk


def not_null(items):
    """:return: iterable of items that are not None or NaN-like"""
    for item in items:
        if item is not None and item == item:
            yield item
