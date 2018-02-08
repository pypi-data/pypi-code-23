# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 12:25:00 2018

@author: twshe
"""
import linq
import keyword


def generate_dual(name):
    title = f'__{name}__' if dual_can_meta[name] else name
    op = name if name not in keyword.kwlist else f'{name}_'
    codes = f"""
        def {title}(self, x):
            if self.right:
                return lambda {name}_right: operator.{op}(x, {name}_right)
            return lambda {name}_left: operator.{op}({name}_left, x)
"""
    return codes


def generate_unary(name):
    title = f'__{name}__' if unary_can_meta[name] else name
    op = name if name not in keyword.kwlist else f'{name}_'
    codes = f"""
        def {title}(self):
            return lambda {name}_item: operator.{op}({name}_item)
"""
    return codes


dual_can_meta = {'add': 1,
                 'truediv': 1,
                 'matmul': 1,
                 'floordiv': 1,

                 'is_': 0,
                 'is_not': 0,
                 'and_': 0,
                 'or_': 0,

                 'and': 1,
                 'or': 1,
                 'xor': 1,
                 'pow': 1,
                 'mod': 1,
                 'mul': 1,
                 'sub': 1,
                 'lt': 1,
                 'le': 1,
                 'eq': 1,
                 'ne': 1,
                 'ge': 1,
                 'gt': 1,
                 'rshift': 1,
                 'lshift': 1
                 }

linq.Flow(dual_can_meta.keys()).Map(generate_dual).Each(print)

unary_can_meta = {
    'invert': 1,
    'neg': 1,
    'not_': 0,
    'pos': 1}

linq.Flow(unary_can_meta.keys()).Map(generate_unary).Each(print)
