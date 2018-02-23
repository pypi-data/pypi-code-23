# -*- coding: utf-8 -*-

###############################################################################
import numpy as np
import unittest

from some_math.geo.points_2D import Points2D

###############################################################################
class TestPoints2D(unittest.TestCase):
    def test_00_rotate_points(self):
        N = 10
        a = 3
        
        x = np.arange(N)
        y = 3 * np.ones(N)
        
        points = Points2D(x, y)
        
        alpha_deg = 45
        alpha = np.radians(alpha_deg)
        m = 1
        n = a / np.cos(alpha)

        rotated_points = points.rotate(alpha)
        x_rot, y_rot = rotated_points.getProfile()
        y_hat = m * x_rot + n

        check = np.allclose(y_rot, y_hat)
        self.assertTrue(check)

        xy_rot = rotated_points.xy
        check = np.allclose(x_rot, xy_rot[:,0])
        self.assertTrue(check)
