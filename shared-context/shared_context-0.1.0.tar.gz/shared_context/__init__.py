from collections import Iterable

import itertools


def create_test(func, context={}):
    def test_to_add(self):
        if callable(context.get("fn")):
            context.get("fn")()
        func(self, **context)

    test_to_add.__name__ = 'test_{func}'.format(func=func.__name__, input=input)
    return test_to_add


def behaves_like(*funcs, **context):
    def decorator(klass):
        list_funcs = _flatten(funcs)
        for func in list_funcs:
            test_to_add = create_test(func, context)
            setattr(klass, test_to_add.__name__, test_to_add)
        return klass

    return decorator


def _flatten(items):
    flat_list = []
    for item in items:
        if isinstance(item, Iterable):
            flat_list += item
        else:
            flat_list.append(item)
    return flat_list
