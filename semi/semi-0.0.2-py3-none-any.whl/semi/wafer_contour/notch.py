# -*- coding: utf-8 -*-

import numpy as np

### relative imports from #####################################################
from line_segment import LineSegment
from outer_circle import OuterCircle

###############################################################################
class Notch:
    def __init__(self, wafer, **kwargs):

        # notch radius and notch depth
        for key, value in kwargs.items():
            if key == 'alpha_notch_deg':
                alpha_notch_deg = value
            elif key == 'r':
                r = value
            elif key == 't':
                t = value

        alpha_notch = np.radians(alpha_notch_deg)
        c, s = np.cos(alpha_notch), np.sin(alpha_notch)
        Rot = np.array(((c, -s), (s, c)))
                
        x_edge = t - r + r / np.sqrt(2)
        
        y_notch = x_edge + r / np.sqrt(2)
        x_notch = np.sqrt(wafer.r**2 - y_notch**2)

        x0 = Rot.dot(np.array((x_notch, y_notch))) - wafer.offset

        x1_left = (
            Rot.dot(np.array((x_notch - x_edge, y_notch - x_edge)))
            - wafer.offset)
        
        self.leftEdge = LineSegment(x0=x0, x1=x1_left)

        x0 = Rot.dot(np.array((x_notch, -y_notch))) - wafer.offset
                    
        x1_right = (
            Rot.dot(np.array((x_notch - x_edge, -y_notch + x_edge)))
            - wafer.offset)
        
        self.rightEdge = LineSegment(x0=x0, x1=x1_right)

        # notch
        # mid point
        x_m = x_notch - t + r
        y_m = 0
        M = Rot.dot(np.array((x_m, y_m))) - wafer.offset
    
        self.outerCircle = OuterCircle(r=r, M=M, x0=x1_right, x1=x1_left)


    def contour(self):
        alpha_deg, a = self.outerCircle.contour()
        
        return alpha_deg, a