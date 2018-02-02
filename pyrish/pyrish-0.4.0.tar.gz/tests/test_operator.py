import pytest
from pyrish.operator import chain_lists, merge_dicts, list_intersection


def test_chain_lists():
    l1 = [1, 2]
    l2 = ['a', 'l']
    l3 = [3.4]
    new_list = chain_lists(l1, l3, l2)
    assert new_list == [1, 2, 3.4, 'a', 'l']


def test_chain_lists_fails():
    with pytest.raises(TypeError):
        chain_lists([1, 2])


def test_merge_dicts():
    d1 = {'a': 1, 'b': 3}
    d2 = {'a': 2, 'd': 'l'}
    d3 = {'c': 4, 'd': 9}
    new_dict = merge_dicts(d1, d2, d3)
    assert new_dict == {'a': 2, 'b': 3, 'c': 4, 'd': 9}


def test_merge_dicts_fails():
    with pytest.raises(TypeError):
        merge_dicts({1: 'a'})


def test_list_intersection():
    l1 = [1, 4, 9, 7, 5, 0]
    l2 = [0, 4, 7, 1, 8, 6]
    intersection = list_intersection(l1, l2)
    assert intersection == [0, 1, 4, 7]

    intersection = list_intersection(l2, l1)
    assert intersection == [0, 1, 4, 7]
