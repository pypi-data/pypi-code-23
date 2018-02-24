#! /usr/bin/env python

import time

from .utils import duration_compact


def time_friendly(delta):
    if delta > 0:
        return duration_compact(delta)
    else:
        return duration_compact(-delta) + ' ago'


def interval_friendly(interval):
    t0, t1 = interval
    if t0:
        d0 = time_friendly(time.time() - t0)
    else:
        d0 = "forever"
    if t1:
        d1 = time_friendly(t1 - time.time())
    else:
        d1 = 'forever'
    return '[%s to %s]' % (d0, d1)


def in_interval(interval, at):
    t0, t1 = interval
    ok1 = t0 is None or t0 <= at
    ok2 = t1 is None or at <= t1
    return ok1 and ok2
