__all__ = ('is_iterable', 'is_sequence', 'is_mapping', 'is_callable')

from typing import Iterable, Sequence, Mapping


def is_iterable(o):
    """Check if the given object ``o`` is of type Iterable
    :param o:
    :return:
    """
    return isinstance(o, Iterable)


def is_sequence(o):
    """Check if the given object ``o`` is of type Sequence

    :param o:
    :return:
    """
    return isinstance(o, Sequence)


def is_mapping(o):
    """Check if the given object ``o`` is of type Mapping

    :param o:
    :return:
    """
    return isinstance(o, Mapping)


def is_callable(o):
    """Check if the given object ``o`` is of type callable

    :param o:
    :return:
    """
    return callable(o)
