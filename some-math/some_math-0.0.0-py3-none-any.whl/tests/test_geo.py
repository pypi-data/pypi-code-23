# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################

from some_math.geo import cart2sph, isLeft, normalized

###############################################################################
class TestGeo(unittest.TestCase):
    def test_00_normalize(self):
        phi_deg = 45
        phi = np.radians(phi_deg)

        theta = np.arccos(1 / np.sqrt(3))
        
        n = normalized((1, 1, 1))
        r_hat, theta, phi_hat = cart2sph(n)
        
        self.assertAlmostEqual(r_hat, 1)
        self.assertAlmostEqual(phi_hat, phi)
        
    def test_01_isLeft(self):
        A = np.array((0, 0, 0))
        B = np.array((1, 0, 0))
        C = np.array((1, 1, 0))
        D = np.array((0, 1, 0))
        F = np.array((0, -1, 0))
        
        check = isLeft(A, B, C, D)
        self.assertTrue(check)
        
        check = isLeft(A, B, C, F)
        self.assertFalse(check)
        
