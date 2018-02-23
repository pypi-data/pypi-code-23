from typing import TypeVar, Generic, Iterable, Callable, List, Iterator

from toolz import reduce, drop, first

T = TypeVar('T')
R = TypeVar("R")


class Seq(Generic[T], Iterable[T]):
    it: Iterable[T]

    @staticmethod
    def of(*items: T) -> "Seq[T]":
        return Seq(items)

    def __init__(self, it: Iterable[T]):
        self.it = it

    def list(self) -> List[T]:
        return list(self.it)

    def map(self, mapper: Callable[[T], R]) -> "Seq[R]":
        return Seq(map(mapper, self.it))

    def filter(self, predicate: Callable[[T], bool]) -> "Seq[T]":
        return Seq(filter(predicate, self.it))

    def reduce(self, reducer: Callable[[R, T], R], initial: R) -> R:
        return reduce(reducer, self.it, initial)

    def tail(self) -> "Seq[T]":
        return Seq(drop(1, self.it))

    def head(self) -> T:
        return first(self.it)

    def index_of(self, predicate: [T, bool]) -> int:
        return next((i for i, v in enumerate(self.it) if predicate(v)), -1)

    def __iter__(self) -> Iterator[T]:
        return self.it.__iter__()


def split_list(predicate: [T, bool], l: List[T]) -> List[List[T]]:
    if len(l) == 0:
        return []

    index = Seq(l).index_of(predicate)

    if index < 0:
        return [l]

    a = l[0:index + 1]
    b = l[index + 1:]

    return [a] + split_list(predicate, b)
