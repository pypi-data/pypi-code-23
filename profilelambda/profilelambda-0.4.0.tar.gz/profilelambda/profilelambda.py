# -*- coding: utf-8 -*-

"""Main module."""
import profilehooks


def profile(func=None, immediate=True):
    if func is None:
        def decorator(fn):
            return profile(fn, immediate=immediate)
        return decorator

    else:
        def wrapper(*args, **kwargs):

            print("Function {!r} got arguments {!r} and keyword arguments {!r}".format(func.__name__, args, kwargs))
            profiled_func = profilehooks.profile(func, immediate=immediate)
            result = profiled_func(*args, **kwargs)
            return result
        return wrapper


@profile(immediate=True)
def plus(a, b):
    return a + b


if __name__ == "__main__":
    print(plus(6, 9))
