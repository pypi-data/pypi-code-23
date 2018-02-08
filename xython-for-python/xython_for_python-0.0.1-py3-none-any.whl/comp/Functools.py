# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 13:39:33 2018

@author: twshe
"""

from xython.comp.FunctionOperator import Holder
import cytoolz

__all__ = ['to_curry',
           'partial',
           'only_if',
           'next_by',
           'before_with',
           'call'
           ]


class FuncOps:
    __slots__ = ['arg', 'ops']

    def __init__(self, arg, ops):
        self.arg = arg
        self.ops = ops

    def __ror__(self, fn):
        return self.ops(fn, self.arg)


def get_to_curry():
    def ops(fn, _):
        return cytoolz.curry(fn)

    return FuncOps(None, ops)


to_curry = get_to_curry()


def partial(*args, **kwargs):
    def ops(fn, arg):
        return lambda head: fn(head, *(arg(head) if isinstance(arg, Holder) else arg for arg in arg[0]), **arg[1])

    return FuncOps((args, kwargs), ops)


def only_if(cond):
    def ops(fn, _):
        new_fn = lambda arg: fn(arg) if cond(arg) else arg
        return new_fn

    return FuncOps(None, ops)


def next_by(next_fn):
    def ops(fn, _):
        return lambda arg: next_fn(fn(arg))

    return FuncOps(None, ops)


def before_with(last_fn):
    def ops(fn, _):
        return lambda *args, **kwargs: fn(last_fn(*args, **kwargs))

    return FuncOps(None, ops)


def call(*args, **kwargs):
    def ops(fn, arg):
        return fn(*arg[0], **arg[1])

    return FuncOps((args, kwargs), ops)
