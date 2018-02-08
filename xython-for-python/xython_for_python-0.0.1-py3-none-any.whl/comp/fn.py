# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 02:38:28 2018

@author: misakawa
"""
from functools import reduce
from xython.comp.FunctionOperator import postfix

__all__ = [
    'and_then',
    'sexpr',
    'identity',
    'flatten',
    'reshape'
]


def identity(e):
    return e


def and_then(*f):
    """
    import xython as xy
    and_then(
            np.transpose | xy.Partial((2, 0, 1)),
            np.shape,
            np.matmul | xy.Partial(hold@np.mean),
            print | xy.Partial(sep=';')
    )(np.array([[1,2], [3,4]])) 
    
    ->
    
    arr = np.array([[1,2], [3,4]])
    arr = np.transpose(arr, (2, 0, 1))
    arr = np.shape(arr)
    arr = np.matmul(arr, np.mean(arr))
    arr = print(arr, sep=';')
    """

    def apply(x):
        return reduce(postfix, f, x)

    return apply


def sexpr(head, *tail):
    """
    pretend to be s-expression.
    sexpr(lambda x, y: x-y, 2, 3) -> -1
    sexpr(
        lambda x: x*2,
        (lambda y, z: y//5 + z, 10, (sum, [1, 2]))) -> (10 // 5 + (sum([1, 2]))) * 2
    """
    if isinstance(head, tuple):
        head = sexpr(*head)

    return head(*map(lambda _: sexpr(*_) if isinstance(_, tuple) else _,
                     tail))


def _reshape(shaper, recursive_types, is_lazy):
    fn_lst = (identity if is_lazy else list)(
        _reshape(e, recursive_types, is_lazy) if e.__class__ in recursive_types else next for e in shaper)
    ret_cls = shaper.__class__

    def apply(itor):
        return ret_cls(fn(itor) for fn in fn_lst)

    return apply


def reshape(shaper, recursive_types=(list, tuple, set), is_lazy=False):
    """
    A lazy reshaper can only be used for once!
    """
    _apply = _reshape(shaper, set(recursive_types), is_lazy)

    def apply(seq, flat=False):
        return _apply(flatten(seq, recursive_types)) if flat else _apply(iter(seq))

    return apply


def flatten(recur_collections, recursive_types=(list,)):
    def _flat(recur):
        for e in recur:
            if e.__class__ in recursive_types:
                yield from _flat(e)
            else:
                yield e

    return _flat(recur_collections)
