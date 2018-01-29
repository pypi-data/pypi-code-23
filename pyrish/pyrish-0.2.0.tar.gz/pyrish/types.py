from typing import Iterable, Sequence, Mapping


def is_iterable(o):
    return isinstance(o, Iterable)


def is_sequence(o):
    return isinstance(o, Sequence)


def is_mapping(o):
    return isinstance(o, Mapping)


def is_callable(o):
    return callable(0)
