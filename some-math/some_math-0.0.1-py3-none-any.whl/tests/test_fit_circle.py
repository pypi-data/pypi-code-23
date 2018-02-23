# -*- coding: utf-8 -*-

###############################################################################
import numpy as np
import unittest

from some_math.fit_circle import CircleFit

###############################################################################
class TestCircleFit(unittest.TestCase):
    def test_00_circleFit(self):
        radius = 10
        N = 20
        
        xc, yc = (5, 3)
        
        alpha = 2 * np.pi * np.random.rand(N)
        r = radius + 0.01 * np.random.randn(N)

        x = xc + r * np.cos(alpha)
        y = yc + r * np.sin(alpha)
        
        circleFit = CircleFit(x, y)

        xc_hat = circleFit.xc
        self.assertAlmostEqual(xc_hat, xc, delta=0.01)

        yc_hat = circleFit.yc
        self.assertAlmostEqual(yc_hat, yc, delta=0.01)

        radius_hat = circleFit.R
        self.assertAlmostEqual(radius_hat, radius, delta=0.01)
        
        residue_hat = circleFit.residue
        self.assertLess(residue_hat, 0.01)
        

