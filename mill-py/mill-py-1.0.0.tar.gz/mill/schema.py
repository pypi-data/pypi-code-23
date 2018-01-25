import json
from collections import Mapping
from functools import reduce
from pkg_resources import resource_string

_schema = json.loads(resource_string("mill", "data/schema.json").decode('utf-8'))


def _process_schema(features):
    out = {}
    for key, value in _flatten(features).items():
        key = key.replace(".value", "")
        try:
            info = _deep_get(_schema, *key.split("."))
            out[info["name"]] = value
        except (TypeError, KeyError):
            pass
    return out


def _deep_get(dictionary, *keys):
    """Deeply get elements from a dict of dicts using an iterable of key values.
    :param dictionary: The dictionary to search.
    :param keys: An iterable (tuple, list, etc) to use as the set of search keys.
    :return: The value at the given key path.
    """
    return reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, keys, dictionary)


def _flatten(dictionary, sep="."):
    """Flatten a dictionary.
    :param dictionary: The dictionary to flatten.
    :param sep: The separator to use in the flat key names.
    :return: A flat dictionary with keys based on the input dict of dicts keys.

    Notes
    -----
    Build a new dictionary from a given one where all non-dict values are left untouched but nested dicts are
    recursively merged in the new one with their keys prefixed by their parent key.

    References
    ----------
    [1]: https://github.com/lrq3000/fdict/blob/master/fdict/fdict.py

    Examples
    --------
    >>> _flatten({1: 42, 'foo': 12})
    {1: 42, 'foo': 12}
    >>> _flatten({1: 42, 'foo': 12, 'bar': {'qux': True}})
    {1: 42, 'foo': 12, 'bar.qux': True}
    >>> _flatten({1: {2: {3: 4}}})
    {'1.2.3': 4}
    >>> _flatten({1: {2: {3: 4}, 5: 6}})
    {'1.2.3': 4, '1.5': 6}
    """
    flat = {}
    dicts = [("", dictionary)]
    while dicts:
        prefix, dictionary = dicts.pop()
        for k, v in dictionary.items():
            k_s = str(k)
            if isinstance(v, Mapping):
                dicts.append(("{}{}{}".format(prefix, k_s, sep), v))
            else:
                k_ = prefix + k_s if prefix else k
                flat[k_] = v
    return flat


def _nest(dictionary, sep="."):
    """Convert to a nested dict.
    :param dictionary: The dictionary to nest.
    :param sep: The separator to use to split the keys.
    :return: A dict of dicts with keys based on the (split at sep) input dict keys.

    Notes
    -----
    Build a dict of dicts from a flat dict, using `sep` to split string-based keys.

    Examples
    --------
    >>> _nest({1: 42, 'foo': 12})
    {1: 42, 'foo': 12}
    >>> _nest({1: 42, 'foo': 12, 'bar.qux': True})
    {1: 42, 'foo': 12, 'bar': {'qux': True}}
    >>> _nest({'1.2.3': 4})
    {1: {2: {3: 4}}}
    >>> _nest({'1.2.3': 4, '1.5': 6})
    {1: {2: {3: 4}, 5: 6}}
    """
    d2 = {}
    # Construct the nested dict for each leaf
    for k, v in dictionary.items():
        # Get all parents of the current leaf, from root down to the leaf's direct parent
        parents = k.split(sep)[:-1]
        # Recursively create each node of this sub-dict branch
        d2sub = d2
        for parent in parents:
            if parent not in d2sub:
                # Create the node if it does not exist
                d2sub[parent] = {}
            # Continue from this node
            d2sub = d2sub[parent]
        # get leaf key
        k = k[k.rfind(sep) + 1:]
        # # set leaf value
        d2sub[k] = v
    return d2
