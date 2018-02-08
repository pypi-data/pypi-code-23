# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 11:51:07 2018

@author: twshe
"""

__all__ = ['fn', '_', 'infix', 'hold']
import operator
from functools import update_wrapper, reduce


class Holder:
    __slots__ = ['x']

    def __init__(self, x=None):
        self.x = x

    @classmethod
    def __matmul__(cls, x):
        return cls(x)


def postfix(a, b):
    return b(a)


class Pipe:
    def __init__(self, f, args, kwargs, f_continue: tuple = None):
        self.f = f
        self.f_continue = f_continue
        self.args = args
        self.kwargs = kwargs
        update_wrapper(self, f)

    def __matmul__(self, other):
        """set an argument"""
        return Pipe(other, self.args, self.kwargs)

    def __pow__(self, kwargs):
        """set kwargs"""
        kwargs.update(self.kwargs)
        return Pipe(self.f, self.args, kwargs, self.f_continue)

    def __mul__(self, args):
        """set varargs"""
        if not isinstance(args, tuple):
            args = tuple(args)
        return Pipe(self.f, self.args + args, self.kwargs)

    def __call__(self, left):

        if not self.f_continue:
            return self.f(left, *self.args, **self.kwargs)
        else:
            return reduce(postfix,
                          self.f_continue,
                          self.f(left, *self.args, **self.kwargs))

    def __ror__(self, left):
        return self(left)

    def __add__(self, then):

        if not callable(then):
            raise ValueError('`callable` expected, but get a `{}` instead.'.format(then.__class__))

        if not self.f_continue:
            return Pipe(self.f, self.args, self.kwargs, (then,))
        else:
            return Pipe(self.f, self.args, self.kwargs, self.f_continue + (then,))

    def __rshift__(self, f):
        return self + f

    def __lshift__(self, arg):
        return Pipe(self.f, self.args + (arg,), self.kwargs)


class Lambda:
    """applicative lambda
    _ = Lambda()
    map(_ + 1, )
    """
    __slots__ = ['right']

    @property
    def r(self):
        return Lambda(right=True)

    def __init__(self, right=False):
        self.right = right

    def __add__(self, x):
        if self.right:
            return lambda add_right: operator.add(x, add_right)
        return lambda add_left: operator.add(add_left, x)

    def __truediv__(self, x):
        if self.right:
            return lambda truediv_right: operator.truediv(x, truediv_right)
        return lambda truediv_left: operator.truediv(truediv_left, x)

    def __matmul__(self, x):
        if self.right:
            return lambda matmul_right: operator.matmul(x, matmul_right)
        return lambda matmul_left: operator.matmul(matmul_left, x)

    def __floordiv__(self, x):
        if self.right:
            return lambda floordiv_right: operator.floordiv(x, floordiv_right)
        return lambda floordiv_left: operator.floordiv(floordiv_left, x)

    def is_(self, x):
        if self.right:
            return lambda is__right: operator.is_(x, is__right)
        return lambda is__left: operator.is_(is__left, x)

    def is_not(self, x):
        if self.right:
            return lambda is_not_right: operator.is_not(x, is_not_right)
        return lambda is_not_left: operator.is_not(is_not_left, x)

    def and_(self, x):
        if self.right:
            return lambda and__right: operator.and_(x, and__right)
        return lambda and__left: operator.and_(and__left, x)

    def or_(self, x):
        if self.right:
            return lambda or__right: operator.or_(x, or__right)
        return lambda or__left: operator.or_(or__left, x)

    def __and__(self, x):
        if self.right:
            return lambda and_right: operator.and_(x, and_right)
        return lambda and_left: operator.and_(and_left, x)

    def __or__(self, x):
        if self.right:
            return lambda or_right: operator.or_(x, or_right)
        return lambda or_left: operator.or_(or_left, x)

    def __xor__(self, x):
        if self.right:
            return lambda xor_right: operator.xor(x, xor_right)
        return lambda xor_left: operator.xor(xor_left, x)

    def __pow__(self, x):
        if self.right:
            return lambda pow_right: operator.pow(x, pow_right)
        return lambda pow_left: operator.pow(pow_left, x)

    def __mod__(self, x):
        if self.right:
            return lambda mod_right: operator.mod(x, mod_right)
        return lambda mod_left: operator.mod(mod_left, x)

    def __mul__(self, x):
        if self.right:
            return lambda mul_right: operator.mul(x, mul_right)
        return lambda mul_left: operator.mul(mul_left, x)

    def __sub__(self, x):
        if self.right:
            return lambda sub_right: operator.sub(x, sub_right)
        return lambda sub_left: operator.sub(sub_left, x)

    def __lt__(self, x):
        if self.right:
            return lambda lt_right: operator.lt(x, lt_right)
        return lambda lt_left: operator.lt(lt_left, x)

    def __le__(self, x):
        if self.right:
            return lambda le_right: operator.le(x, le_right)
        return lambda le_left: operator.le(le_left, x)

    def __eq__(self, x):
        if self.right:
            return lambda eq_right: operator.eq(x, eq_right)
        return lambda eq_left: operator.eq(eq_left, x)

    def __ne__(self, x):
        if self.right:
            return lambda ne_right: operator.ne(x, ne_right)
        return lambda ne_left: operator.ne(ne_left, x)

    def __ge__(self, x):
        if self.right:
            return lambda ge_right: operator.ge(x, ge_right)
        return lambda ge_left: operator.ge(ge_left, x)

    def __gt__(self, x):
        if self.right:
            return lambda gt_right: operator.gt(x, gt_right)
        return lambda gt_left: operator.gt(gt_left, x)

    def __invert__(self):
        return lambda invert_item: operator.invert(invert_item)

    def __neg__(self):
        return lambda neg_item: operator.neg(neg_item)

    def not_(self):
        return lambda not__item: operator.not_(not__item)

    def __pos__(self):
        return lambda pos_item: operator.pos(pos_item)

    def __rshift__(self, x):
        if self.right:
            return lambda rshift_right: operator.rshift(x, rshift_right)
        return lambda rshift_left: operator.rshift(rshift_left, x)

    def __lshift__(self, x):
        if self.right:
            return lambda lshift_right: operator.lshift(x, lshift_right)
        return lambda lshift_left: operator.lshift(lshift_left, x)


fn = _ = Lambda()
infix = Pipe(lambda _: _, (), {})
hold = Holder()
