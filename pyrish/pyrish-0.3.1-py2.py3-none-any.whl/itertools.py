__all__ = (
    'isplit',
    'first',
    'last',
    'last_n',
    'filter_n'
)

import itertools as it
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Optional,
    Iterator
)

from collections import deque
from re import finditer

from .exceptions import EmptyIterableError
from .types import is_sequence


def isplit(s: str, sep: Optional[str] = '') -> Iterator[Any]:
    """Return a list of the words from ``s``, using ``sep`` as the delimiter.
    If ``sep`` is not specified or is None, whitespace is used a separator
    and empty strings are removed from the result.

    :param (str) s: string to be splited into the list of words
    :param (str) sep: delimiter
    :return: Iterator[Any]

    Usage::

        >>> first(isplit('#ln;dsfg#dfsgs#', sep='#'))
        'ln;dsfg'
        >>> list(isplit('#ln;dsfg#dfsgs#', sep='#'))
        ['ln;dsfg', 'dfsgs']
    """

    def finder_pattern():
        if not sep:
            return r'.?'
        return r'[^{sep}]*'.format(sep=sep)

    pattern = finder_pattern()
    items = (x.group(0) for x in finditer(pattern, s) if x.group(0))
    return items


def first(iterable: Iterable, condition: Optional[Callable] = None) -> Any:
    """Returns the first item in the `iterable` that
    satisfies the `condition`.

    If the condition is not given, returns the first item of
    the iterable.

    Raises `EmptyIterableError` if iterable is empty or
    no item satisfying the condition is found.

    :param iterable:  an iterable object
    :param condition: a test function used to filter out items from the iterable
    :return: Any

    Usage::

        >>> first((1,2,3), condition=lambda x: x % 2 == 0)
        2
        >>> first(range(3, 100))
        3
        >>> first( () )
        Traceback (most recent call last):
        ...
        EmptyIterableError
    """
    try:

        if not condition:
            if is_sequence(iterable):
                return iterable[0]
            return next(iterable)

        return next(x for x in iterable if condition(x))
    except (StopIteration, IndexError) as _:
        raise EmptyIterableError()


def last(iterable: Iterable) -> Any:
    """Returns the last item of the given the ``iterable``.

    :param iterable:  an iterable object
    :param condition: a test function used to filter out items from the iterable
    :return:
    """
    try:
        result = last_n(iterable, 1)
        return next(result)
    except StopIteration as _:
        raise EmptyIterableError()


def last_n(iterable: Iterable, n: int) -> Generator[Any, None, None]:
    """Returns the last ``n`` items of the given  ``iterable``.

    :param iterable:  an iterable object
    :param n: the number of items to be returned
    :return: Generator[Any, None, None]

    Usage::

        >>> data = [1,234,234,235,3465,342,3,4,2345,2345,2345]
        >>> last_n(data, 3)
        <generator object last_n at 0x109653830>
        >>> list(last_n(data, 3))
        [2345,2345,2345]
    """

    if is_sequence(iterable):
        iterable = iterable[-n:]
    else:
        iterable = deque(iterable, maxlen=n)

    for i in iterable:
        yield i


def filter_n(condition: Callable, iterable: Iterable, n: Optional[int] = 0) -> Iterable:
    """Return an iterator yielding the first ``n`` items of iterable that
    satisfies ``condition(item)``. If ``n`` not given or equal zero it returns
    all items that satisfies the test function.

    :param condition: a test function used to filter out items from the iterable
    :param iterable:  an iterable object
    :param n: the number of items to be returned
    :return:

    Usage::

        >>> data = [1,234,234,235,3465,342,3,4,2345,2345,2345]
        >>> filter_n(lambda x: x % 5 == 0, data)
        <filter at 0x102de6630>
        >>> list(filter_n(lambda x: x % 5 == 0, data))
        [235, 3465, 2345, 2345, 2345]
        >>> list(filter_n(lambda x: x % 5 == 0, data, n=3))
        [235, 3465, 2345]
        >>> list(filter_n(lambda x: x % 5 == 0, [], n=3))
        []
    """

    if not n:
        return filter(condition, iterable)

    counter = it.count()

    def _condition_with_counter(x):
        if not condition(x):
            # don't increment counter
            return False
        count = next(counter)
        return count < n

    return filter(_condition_with_counter, iterable)
