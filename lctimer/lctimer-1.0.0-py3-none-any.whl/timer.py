# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time


_TIMER = {}


def _isfunction(func):
    def _f():
        pass
    return isinstance(func, type(_f))


def _scale(best, aver, worst):
    if best > 1e3 and worst > 1e6:
        return 's', best / 1e6, aver / 1e6, worst / 1e6
    elif best > 1e3 and worst > 1e3:
        return 'ms', best / 1e3, aver / 1e3, worst / 1e3
    return 'μs', best, aver, worst


def sum_up(keep_num=10):
    max_n = []
    for func_name, records in _TIMER.items():
        aver = sum(records['timer']) / records['counter']
        max_n.append((aver, func_name))
        if len(max_n) > keep_num:
            max_n.sort(reverse=True)
            max_n.pop()
    max_n.sort(reverse=True)
    for aver, func_name in max_n:
        best = min(_TIMER[func_name]['timer'])
        worst = max(_TIMER[func_name]['timer'])
        loop = _TIMER[func_name]['counter']
        unit, best, aver, scale = _scale(best, aver, worst)
        print(
            'Function: "{0}"\t\tBest: {2:.2f} {5}\t\tAverage: {3:.2f} {5}\t\tWorst: {4:.2f}'
            ' {5}\t\tTotal Loops: {1}'.format(func_name, loop, best, aver, scale, unit)
        )


def record(obj):
    if _isfunction(obj):
        return _record_fn(obj)
    else:
        try:
            return _record_cls(obj)
        except:
            pass


def _record_fn(func):
    def wrap(*args, **kwargs):
        global _TIMER
        start_at = time.time()
        result = func(*args, **kwargs)
        if func.__name__ not in _TIMER:
            _TIMER[func.__name__] = dict(
                timer=[(time.time() - start_at) * 1e6],
                counter=1,
            )
        else:
            _TIMER[func.__name__]['timer'].append((time.time() - start_at) * 1e6)
            _TIMER[func.__name__]['counter'] += 1
        return result
    wrap.__name__ = func.__name__
    return wrap


def _record_cls(cls):
    for pub_func in dir(cls):
        if not pub_func.startswith('_') and hasattr(getattr(cls, pub_func), '__call__'):
            setattr(cls, pub_func, _record_fn(getattr(cls, pub_func)))
    return cls
