import pytest

from pyrish.types import is_iterable, is_sequence, is_mapping, is_callable


@pytest.mark.parametrize('obj, result', [
    ([1, 2, 3, 4], True),
    ([], True),
    ((9, 7), True),
    (iter([1, 2, 3, 4]), True),
    (range(45, 50), True),
    ('sfgdasdg', True),
    ({3, 4}, True),
    ({'a': 1}, True),
])
def test_is_iterable(obj, result):
    assert is_iterable(obj) == result


@pytest.mark.parametrize('obj, result', [
    ([1, 2, 3, 4], True),
    ([], True),
    ((9, 7), True),
    (iter([1, 2, 3, 4]), False),
    (range(45, 50), True),
    ('sfgdasdg', True),
    ({3, 4}, False),
    ({'a': 1}, False),
])
def test_is_sequence(obj, result):
    assert is_sequence(obj) == result


@pytest.mark.parametrize('obj, result', [
    ([1, 2, 3, 4], False),
    ((9, 7), False),
    ({}, True),
    ({'a': 1}, True),
])
def test_is_mapping(obj, result):
    assert is_mapping(obj) == result


@pytest.mark.parametrize('obj, result', [
    ([1, 2, 3, 4], False),
    (Exception, True),
    (lambda x: x + 1, True),
    (map, True)
])
def test_is_callable(obj, result):
    assert is_callable(obj) == result
