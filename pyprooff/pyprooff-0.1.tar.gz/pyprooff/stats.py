#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np


def derivative(ys, xs=None):
    """Calculates the difference-based derivative of a series of numbers.

    Args:
        ys: the y term in dy/dx
        xs: the x term in dy/dx; if None, each dx = 1

    Returns:
        list of numbers with length 1 less than ys and xs
    """
    if xs is None:
        xs = range(len(ys))
    assert len(ys) == len(xs)
    derivative = []
    for x1, x2, y1, y2 in zip(xs[:-1], xs[1:], ys[:-1], ys[1:]):
        derivative.append((y2 - y1) * 1.0 / (x2 - x1))
    return derivative
