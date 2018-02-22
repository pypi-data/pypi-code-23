# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################
from numpy.linalg import norm

from some_math.fit_plane import fitPlane
from some_math.quaternion import Quaternion

###############################################################################
class TestPlaneFit(unittest.TestCase):
    def test_00_001_plane(self):
        N = 500
        a = 3 # distance from origin
        n = np.array((0, 0, 1))
        
        xmin, xmax = (-10, 10)
        ymin, ymax = (-10, 10)
        
        x0 = (xmax - xmin) * np.random.rand(N) - xmax
        y0 = (ymax - ymin) * np.random.rand(N) - ymax
        z0 = a * np.ones(N) + 0.001 * np.random.randn(N)
        
        XYZ = np.vstack((x0, y0, z0)).T
        
        n_hat, a_hat = fitPlane(XYZ)
        
        self.assertAlmostEqual(a, a_hat, places=3)
        
        check = np.allclose(n_hat, n, atol=1E-3)
        self.assertTrue(check)
        
        
    def test_01_110_Plane(self):
        N = 500
        a = 1
        n = np.array((1, 1, 0))
        n = n / norm(n)
        n_xy = n[0]
        
        X = 10 * np.random.rand(N)
        Y = a / n_xy - X + 0.001 * np.random.randn(N)
        Z = 10 * np.random.rand(N)
        XYZ = np.vstack((X, Y, Z)).T
        
        n_hat, a_hat = fitPlane(XYZ)

        self.assertAlmostEqual(a, a_hat, places=3)

        check = np.allclose(n_hat, n, atol=1E-3)
        self.assertTrue(check)

    def test_02_111_Plane(self):
        N = 500
        a = 1
        n = np.array((1, 1, 1))

        n = n / norm(n)
        ni = n[0]

        X = 10 * np.random.rand(N)
        Y = 10 * np.random.rand(N)
        Z = a / ni - X - Y

        XYZ = np.vstack((X, Y, Z)).T
        
        n_hat, a_hat = fitPlane(XYZ)

        self.assertAlmostEqual(a, a_hat, places=3)
        
        check = np.allclose(n_hat, n)
        self.assertTrue(check)

    def test_03_linspace(self):
        M = 40
        N = 20

        a = 3 # distance from origin
        n = np.array((1, 1, 1))
        n = n / norm(n)
        
        xmin, xmax = (0, 10)
        ymin, ymax = (0, 20)
        
        x = np.linspace(xmin, xmax, M, endpoint=False)
        y = np.linspace(ymin, ymax, N, endpoint=False)
        
        X, Y = np.meshgrid(x, y, indexing='ij')
        Z = a * np.ones((M, N)) + 0.001 * np.random.randn(N)

        X_flat = X.flatten()
        Y_flat = Y.flatten()
        Z_flat = Z.flatten()
        
        XYZ = np.vstack((X_flat, Y_flat, Z_flat)).T

        ez = np.array((0, 0, 1))
        q = Quaternion.from_v_v(ez, n)
        R = q.as_rotation_matrix()
        XYZ_rotated = np.array(R * XYZ.T).T
                          
        n_hat, a_hat = fitPlane(XYZ_rotated)
        
        self.assertAlmostEqual(a, a_hat, places=2)
        
        check = np.allclose(n_hat, n, atol=1E-3)
        self.assertTrue(check)