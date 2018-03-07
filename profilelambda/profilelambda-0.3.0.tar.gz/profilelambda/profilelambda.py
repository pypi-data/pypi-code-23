# -*- coding: utf-8 -*-

"""Main module."""
from profilehooks import profile as _profile


def profile(func):
    def wrapper(*args, **kwargs):
        print("Function {!r} got arguments {!r} and keyword arguments {!r}".format(func.__name__, args, kwargs))
        profiled_func = _profile(func)
        result = profiled_func(*args, **kwargs)
        return result
    return wrapper


@profile
def plus(a, b):
    return a + b


if __name__ == "__main__":
    print(plus(6, 9))
