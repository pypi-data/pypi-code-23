from typing import Generator

import pytest

from pyrish.exceptions import EmptyIterableError
from pyrish.itertools import isplit, first, last_n, last, filter_n


# @@@@@@ testing isplit @@@@@@

@pytest.mark.parametrize('string, sep, length, expected_list', [
    ('#ln;dsfg####dfsgs##', '#', 2, ['ln;dsfg', 'dfsgs']),
    ('http://www.site.de/verzeichnis/unterverzeichnis', '/', 4,
     ['http:', 'www.site.de', 'verzeichnis', 'unterverzeichnis']),
    ('', '*', 0, []),
])
def test_isplit_non_empty_separator(string, sep, length, expected_list):
    result = isplit(string, sep=sep)
    assert isinstance(result, Generator)
    result_list = list(result)
    assert len(result_list) == length
    assert result_list == expected_list


@pytest.mark.parametrize('string, length, expected_list', [
    ('test', 4, ['t', 'e', 's', 't']),
    ('', 0, []),
])
def test_isplit_empty_separator(string, length, expected_list):
    result = isplit(string)
    assert isinstance(result, Generator)
    result_list = list(result)
    assert len(result_list) == length
    assert result_list == expected_list


# @@@@@@ testing first @@@@@@

@pytest.mark.parametrize('obj, result, condition', [
    (range(3, 100), 3, None),
    (iter((11, 21, 31)), 11, None),
    ([11, 13, 25, 34], 25, lambda x: x % 5 == 0),
])
def test_first(obj, result, condition):
    x = first(obj, condition)
    assert x == result


@pytest.mark.parametrize('obj, condition', [
    ([], None),
    ([11, 13, 27, 31], lambda x: x % 5 == 0),
])
def test_first_raises_stop_iteration(obj, condition):
    with pytest.raises(EmptyIterableError):
        first(obj, condition)


# @@@@@@ testing last_n @@@@@@

@pytest.mark.parametrize('obj, n, expected_list', [
    ([11, 13, 27, 31, 45, 89], 3, [31, 45, 89]),
    (iter(['wdf', 'wer', 'cvb', 'tuy', 'fgh']), 2, ['tuy', 'fgh']),
    ([11, 13, 27, 31, 45, 89], 7, [11, 13, 27, 31, 45, 89]),
    (iter(['wdf', 'wer', 'cvb', 'tuy', 'fgh']), 0, []),
    ([], 1, [])
])
def test_last_n(obj, n, expected_list):
    result = last_n(obj, n)
    assert isinstance(result, Generator)
    result_list = list(result)
    assert result_list == expected_list


# @@@@@@ testing last @@@@@@

def test_last_with_non_empty_list():
    assert last([11, 13, 27, 31, 45, 89]) == 89


def test_last_with_empty_list():
    with pytest.raises(EmptyIterableError):
        last([])


# @@@@@@ testing filter_n @@@@@@

@pytest.mark.parametrize('condition, obj, n, expected_list', [
    (lambda x: x % 5 == 0, [1, 235, 234, 3, 4, 45, 345, 2345], 3, [235, 45, 345]),
    (lambda x: x % 5 == 0, [1, 9, 234, 3, 4, 2341, 23, 2345, 5], 2, [2345, 5]),
    (lambda x: x % 5 == 0, [1, 15, 234, 3, 4, 2341, 23, 2345, 5], 0, [15, 2345, 5]),
    (lambda x: x % 5 == 0, [5], 4, [5]),
    (lambda x: x % 5 == 0, [], 2, []),
])
def test_filter_n(condition, obj, n, expected_list):
    result = filter_n(condition, obj, n)
    assert list(result) == expected_list
