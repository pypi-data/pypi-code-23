# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################
from some_math.geo import normalized
from some_math.geo.points_3D import Points3D
from some_math.fit_plane import fitPlane

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
        n = normalized((1, 1, 0))
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
        n = normalized((1, 1, 1))
        ni = n[0]

        X = 10 * np.random.rand(N)
        Y = 10 * np.random.rand(N)
        Z = a / ni - X - Y

        XYZ = np.vstack((X, Y, Z)).T
        
        n_hat, a_hat = fitPlane(XYZ)

        self.assertAlmostEqual(a, a_hat, places=3)
        
        check = np.allclose(n_hat, n)
        self.assertTrue(check)

    def test_03_point3d(self):
        M, N = shape = (40, 20)
        a = 3 # distance from origin
        n = normalized((1, 1, 1))
        
        xmin, xmax = (0, 10)
        ymin, ymax = (0, 20)
        
        x = np.linspace(xmin, xmax, M, endpoint=False)
        y = np.linspace(ymin, ymax, N, endpoint=False)
        
        X, Y = np.meshgrid(x, y, indexing='ij')
        Z = a * np.ones(shape) + 0.001 * np.random.randn(M, N)

        ez = np.array((0, 0, 1))
        P = Points3D((X, Y, Z)).rotate_v_v(ez, n)
        n_hat, a_hat = fitPlane(P.XYZ)
        
        self.assertAlmostEqual(a, a_hat, places=2)
        
        check = np.allclose(n_hat, n, atol=1E-3)
        self.assertTrue(check)
        