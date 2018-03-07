
from collections import defaultdict
from pandas import DataFrame
from copy import deepcopy
from typing import Dict, List, NewType


TypeDataFrame = NewType('TypeDataFrame', DataFrame)


def as_dataframe(obj: Dict or List[Dict]) -> TypeDataFrame:
    """ Returns dataframe built from dictionary or list of dictionaries.

    :param obj: Dictionary or list of dictionaries.
    :returns: Dataframe.
    """

    if isinstance(obj, dict):
        obj = [obj]

    combined_df = DataFrame()
    for d in obj:
        num_rows = max([1] + [len(d[k]) for k in d if isinstance(d[k], list)])
        df = DataFrame(_flattened(d), index=range(num_rows))
        combined_df = combined_df.append(df, ignore_index=False, verify_integrity=False)

    combined_df = combined_df.reset_index(drop=True)
    combined_df = combined_df.dropna(axis='columns', how='all')
    return combined_df


def _flattened(nested_dict: dict) -> dict:
    """ Returns flattened dictionary

    :param nested_dict: Nested dictionary. A nested dictionary is a dictionary with at least one value being a
    dictionary that itself may be nested, ad infinitum. E.g.: `{'a': 1, 'b': {'c': 2, 'd': 3}}`.
    :returns: Flattened dictionary.
    """

    flat = dict()

    for k, v in nested_dict.items():
        if isinstance(v, dict):
            new = _flattened(v)
            flat.update({str(k) + '.' + kk: new[kk] for kk in new})
        elif isinstance(v, list):
            if all([isinstance(el, dict) for el in v]):
                new = _single_dict(v)
                new = _flattened(new)
                flat.update({str(k) + '.' + kk: new[kk] for kk in new})
            else:
                flat.update({k: v})
        else:
            flat.update({k: v})
    return flat


def _single_dict(dicts: list, missing_value: str=None) -> dict:
    """ Returns a single dictionary built from a list of dictionaries

    :param dicts: List of dictionaries. The dictionaries are allowed to be heterogeneous.
    :param missing_value: How to represent missing values when the dictionaries are heterogeneous.
    :returns: A single dictionary.
    """

    dicts = deepcopy(dicts)

    for i in range(len(dicts)):
        dicts[i] = _flattened(dicts[i])

    keys = set([key for d in dicts for key in list(d.keys())])
    dictionary = dict(zip(keys, [list() for i in range(len(keys))]))

    for d in dicts:
        new = defaultdict(lambda: missing_value, **d)
        for k in keys:
            dictionary[k].append(new[k])

    return dictionary
