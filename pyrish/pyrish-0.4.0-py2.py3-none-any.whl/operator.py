from typing import List, Dict

import functools as ft


def _chain_2_lists(l1: List, l2: List):
    """Unpack l1 and l2 into new one list"""
    return [*l1, *l2]


def chain_lists(*args: List) -> List:
    """Generates new list by appending elements from the given
    list of list. Elements are added in the order the lists are given.

    :param args: lists to be chained
    :return:
    """

    if len(args) < 2:
        raise TypeError(f'merge_lists expected at least 2 arguments, got {len(args)}')

    return ft.reduce(_chain_2_lists, args)


def _merge_2_dicts(d1: Dict, d2: Dict):
    """Unpack d1 and d2 into new dict"""
    return {**d1, **d2}


def merge_dicts(*args: Dict) -> Dict:
    """Generates new dict from the list lof given dicts.
    The order matters, if a key exists in more than dict
    it's latest value will be considered.

    :param args:dicts to be merged
    :return:
    """

    if len(args) < 2:
        raise TypeError(f'merge_dicts expected at least 2 arguments, got {len(args)}')

    return ft.reduce(_merge_2_dicts, args)


def list_intersection(l1: List, l2: List):
    """Returns list of commun elements between two lists"""

    intersection = set(l1) & set(l2)
    return list(intersection)
