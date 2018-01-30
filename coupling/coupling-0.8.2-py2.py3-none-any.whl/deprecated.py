# coding: utf-8

import inspect
import warnings
import functools


string_types = (type(b''), type(u''))


def _wrap(func, msg):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)     # turn off filter
        warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)    # reset filter
        return func(*args, **kwargs)
    return new_func


class Deprecated(object):
    def __init__(self, reason=None):
        self.reason = reason

    def __call__(self, item):
        if inspect.isclass(item) or inspect.isfunction(item) or inspect.ismethod(item):
            fmt = "Call to deprecated {}"
            if self.reason:
                fmt += " ({})"
            msg = fmt.format(item.__name__, self.reason)
            return _wrap(item, msg)
        elif isinstance(item, string_types):
            reason = item
            return self.__class__(reason)
        else:
            pass


deprecated = Deprecated()
