# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

from line_segment import LineSegment

###############################################################################
class Flat(LineSegment):
    def __init__(self, wafer, **kwargs):
        
        for key, value in kwargs.items():
            if key == 'alpha_deg':
                alpha = np.radians(value)
            elif key == 'length':
                length = value

        n = np.array((np.cos(alpha), np.sin(alpha)))
        p = np.array((-np.sin(alpha), np.cos(alpha)))

        a_wafer = np.sqrt(wafer.r**2 - length**2 / 4)
        a_off = a_wafer - np.dot(n, wafer.offset)

        x0 = a_wafer * n - length / 2 * p - wafer.offset
        x1 = a_wafer * n + length / 2 * p - wafer.offset

        kwargs_linesegment = {}
        kwargs_linesegment['a'] = a_off
        kwargs_linesegment['normal'] = n
        kwargs_linesegment['x0'] = x0
        kwargs_linesegment['x1'] = x1
        
        super(Flat, self).__init__(**kwargs_linesegment)