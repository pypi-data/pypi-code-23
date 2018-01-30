"""Utility functions."""

# This module should have no dependencies on other menhir modules

# Multi-dispatch functions for python
# Modified from https://gist.github.com/adambard/6bf15282874ca89404f7


def multi(dispatch_fn, default=None):
    """Decorate a function to dispatch on.

    The value returned by the dispatch function is used to look up the
    implementation function based on its dispatch key.
    """
    def _inner(*args, **kwargs):
        dispatch_value = dispatch_fn(*args, **kwargs)
        f = _inner.__multi__.get(dispatch_value, _inner.__multi_default__)
        if f is None:
            raise Exception(
                "No implementation of %s for dispatch value %s" % (
                    dispatch_fn.__name__,
                    dispatch_value
                )
            )
        return f(*args, **kwargs)

    _inner.__multi__ = {}
    _inner.__multi_default__ = default
    return _inner


def method(dispatch_fn, dispatch_key=None):
    """Decorate a function implementing dispatch_fn for dispatch_key.

    If no dispatch_key is specified, the function is used as the
    default dispacth function.
    """
    def apply_decorator(fn):
        if dispatch_key is None:
            # Default case
            dispatch_fn.__multi_default__ = fn
        else:
            dispatch_fn.__multi__[dispatch_key] = fn
        return dispatch_fn
    return apply_decorator


def reductions(f, lst, init):
    """Like reduce, but returns all intermediate values as a sequence."""
    prev = init
    for i in lst:
        prev = f(prev, i)
        yield prev


# http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
# merges b into a

def deep_merge(a, b, path=None):
    """Deep merge b into a.

    Modifies a.  Returns the modified dict a.
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deep_merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key].extend(b[key])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def getd(d, k):
    """Get a dict from key, k, of dict, d, creating a dict if needed.

    This function replaces the `v = d.get(k,{}); d[k] = v` pattern.
    """
    value = d.get(k)
    if value is None:
        value = d[k] = {}
    return value


def select_keys(d, ks):
    """Return a dict containing just the specified keys, ks, from d."""
    return {k: d[k] for k in ks if k in d}


try:
    _basestring = basestring
except NameError:
    _basestring = str


def is_string(x):
    """Predicate for value being a string."""
    return isinstance(x, _basestring)
