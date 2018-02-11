# coding=utf-8
"""
Tests random package
"""

from hypothesis import given, strategies as st

from elib.custom_random import random_bytes, random_string


def test_random_str():
    res = set()
    for _ in range(10000):
        rand = random_string()
        assert len(rand) == 6
        assert rand not in res
        res.add(rand)


def test_random_bytes():
    res = set()
    for _ in range(100000):
        rand = random_bytes()
        assert len(rand) == 1024
        assert rand not in res
        res.add(rand)


@given(length=st.integers(min_value=1, max_value=1024))
def test_random_string_length(length):
    assert len(random_string(length)) == length
