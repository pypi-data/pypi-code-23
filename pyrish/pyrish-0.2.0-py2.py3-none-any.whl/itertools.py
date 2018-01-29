import itertools as it
from collections import deque
from re import finditer
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Optional
)

from pyrish.types import is_sequence


def isplit(s: str, sep: Optional[str] = '') -> Generator[Any, None, None]:
    def finder_pattern():
        if not sep:
            return r'.?'
        return r'[^{sep}]*'.format(sep=sep)

    pattern = finder_pattern()
    items = (x.group(0) for x in finditer(pattern, s) if x.group(0))
    return items


def first(iterable: Iterable, condition: Optional[Callable] = None) -> Any:
    if not condition:
        if is_sequence(iterable):
            return iterable[0]
        return next(iterable)

    return next(x for x in iterable if condition(x))


def last(iterable: Iterable) -> Any:
    result = last_n(iterable, 1)
    return next(result)


def last_n(iterable: Iterable, n: int) -> Generator[Any, None, None]:
    if is_sequence(iterable):
        iterable = iterable[-n:]
    else:
        iterable = deque(iterable, maxlen=n)

    for i in iterable:
        yield i


def filter_n(condition: Callable, iterable: Iterable, n: int = 0) -> Iterable:
    if not n:
        return filter(condition, iterable)

    counter = it.count()

    def _condition_with_counter(x):
        if not condition(x):
            return False

        count = next(counter)
        return count < n

    return filter(_condition_with_counter, iterable)
