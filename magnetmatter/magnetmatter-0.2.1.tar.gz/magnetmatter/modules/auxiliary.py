# auxiliary.py

import re

def cm2inch(*tupl):
    """
    Helper function to convert figsize-cm-tuple to inches.

    Args:
        tuple or list of tupe that will have all its elements converted to
        metric dimensions.

    Returns:
        A new tuple with metric dimensions.

    """
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)

def natural_keys(text):
    """
    Returns a list of chars and digits that can be used for sorting algorithms.

    Args:
        text: string containing any symbols.

    Returns:
        A list of symbols that - if possible - has it character converted to
        integer datatype to allow human-like sorting.

    Usecase 1:
        alist.sort(key=natural_keys)
    Usecase 2:
        alist = sorted(alist, key = natural_keys)

    """
    atoi = lambda c: int(c) if c.isdigit() else c
    return [ atoi(c) for c in re.split('(\d+)', text) ]
