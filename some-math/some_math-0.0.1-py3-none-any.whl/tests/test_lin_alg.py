# -*- coding: utf-8 -*-

###############################################################################
import numpy as np
import unittest

from some_math.geo import normalized
from some_math.lin_alg import findPointsAbove, findPointsBelow
from some_math.lin_alg import findPointsInAxisRange, findPointsInRange

###############################################################################
class TestPlaneFit(unittest.TestCase):
    def test_00_findPointsInRange(self):
        x = 1 + np.r_[0, 1, 2, 3] + 1E-4 * np.random.randn(4)
        y = 1 - np.r_[0, 1, 2, 3] + 1E-4 * np.random.randn(4)
        dataPoints = np.vstack((x, y)).T
        
        alpha_deg = 45
        alpha = np.radians(alpha_deg)
        nx = np.cos(alpha)
        ny = np.sin(alpha)
        n = np.array((nx, ny))

        a = np.sqrt(2)
        tol = 0.01

        plane = findPointsInRange(dataPoints, n, a, tol)

        N = len(plane)
        
        self.assertEqual(N, 4)


    def test_01_findPointsInAxisRange(self):
        x = np.r_[1, 2, 3, 4]
        y = np.r_[0, 1, 2, 3]
        dataPoints = np.vstack((x, y)).T

        px = findPointsInAxisRange(dataPoints, (0, 4))
        Nx = len(px)

        self.assertEqual(Nx, 3)

        py = findPointsInAxisRange(dataPoints, (0, 4), axis=1)
        Ny = len(py)
        
        self.assertEqual(Ny, 3)

    def test_02_findPointsBelow(self):
        a = 3
        below = 2
        above = 4
        
        nx, ny, nz = n = normalized((1, 1, 1))

        x = np.r_[1, 2, 3, 4]
        y = np.r_[0, 1, 2, 3]
        z = (a - nx * x - ny * y) / nz
            
        dataPoints = np.vstack((x, y, z)).T

        P = findPointsBelow(dataPoints, n, below)
        N = len(P)
        self.assertEqual(N, 0)

        P = findPointsBelow(dataPoints, n, above)
        N = len(P)
        self.assertEqual(N, 4)

    def test_03_findPointsAbove(self):
        a = 3
        below = 2
        above = 4
        
        nx, ny, nz = n = normalized((1, 1, 1))

        x = np.r_[1, 2, 3, 4]
        y = np.r_[0, 1, 2, 3]
        z = (a - nx * x - ny * y) / nz
            
        dataPoints = np.vstack((x, y, z)).T

        P = findPointsAbove(dataPoints, n, below)
        N = len(P)
        self.assertEqual(N, 4)

        P = findPointsAbove(dataPoints, n, above)
        N = len(P)

        self.assertEqual(N, 0)

