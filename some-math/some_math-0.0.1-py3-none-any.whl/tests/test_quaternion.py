# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################
from numpy.linalg import norm
from some_math.quaternion import Quaternion

###############################################################################
class TestPlaneFit(unittest.TestCase):
    def test_00_representation(self):
        x, y, z = np.eye(3)
        q = Quaternion.from_v(x)
        q_str = str(q)

        self.assertTrue('Quaternion:' in q_str)

    def test_01_permutations(self):
        x, y, z = np.eye(3)

        theta_deg = 120
        theta = np.radians(theta_deg)
        
        n = np.array((1, 1, 1))
        n = n / norm(n)

        Q = Quaternion.from_v_theta(n, theta)
        Q_inv = Quaternion.inverse(Q)
        
        X = Quaternion.from_v(x)
        Y = Quaternion.from_v(y)
        Z = Quaternion.from_v(z)
        
        Y_hat = Q * X * Q_inv
        Z_hat = Q * Y * Q_inv
        X_hat = Q * Z * Q_inv

        self.assertAlmostEqual(X_hat.x[0], 0)
        self.assertAlmostEqual(Y_hat.x[0], 0)
        self.assertAlmostEqual(Z_hat.x[0], 0)
        
        self.assertAlmostEqual(X_hat.x[1], 1)
        self.assertAlmostEqual(X_hat.x[2], 0)
        self.assertAlmostEqual(X_hat.x[3], 0)

        self.assertAlmostEqual(Y_hat.x[1], 0)
        self.assertAlmostEqual(Y_hat.x[2], 1)
        self.assertAlmostEqual(Y_hat.x[3], 0)
        
        self.assertAlmostEqual(Z_hat.x[1], 0)
        self.assertAlmostEqual(Z_hat.x[2], 0)
        self.assertAlmostEqual(Z_hat.x[3], 1)

    def test_02_vector(self):
        v = np.array((1, 1, 1))
        v = v / norm(v)
        v_q = Quaternion.from_v(v)
        r, theta, phi = v_q.spherical()

        phi_deg = np.rad2deg(phi)
        theta_deg = np.rad2deg(theta)

        self.assertAlmostEqual(r, 1)

        self.assertAlmostEqual(phi_deg, 45)

        theta_hat = np.arctan2(1, np.sqrt(2))
        theta_hat_deg = np.rad2deg(theta_hat)
        self.assertAlmostEqual(theta_hat_deg, theta_deg)

    def test_03_from_v_v(self):
        x, y, z = np.eye(3)

        alpha_deg = 90
        alpha = np.radians(alpha_deg)

        q = Quaternion.from_v_v(x, y)

        self.assertAlmostEqual(q.x[0], np.cos(alpha/2))
        self.assertAlmostEqual(q.x[1], 0)
        self.assertAlmostEqual(q.x[2], 0)
        self.assertAlmostEqual(q.x[3], np.sin(alpha/2))

    def test_04_rotationMatrix(self):
        alpha_deg = 45
        alpha = np.radians(alpha_deg)
        q = Quaternion.from_v_theta((0, 0, 1), alpha)
        
        R = q.as_rotation_matrix()

        s = np.sin(alpha)
        c = np.cos(alpha)

        self.assertAlmostEqual(R[0, 0], c)
        self.assertAlmostEqual(R[0, 1], -s)
        self.assertAlmostEqual(R[0, 2], 0)
        self.assertAlmostEqual(R[1, 0], s)
        self.assertAlmostEqual(R[1, 1], c)
        self.assertAlmostEqual(R[1, 2], 0)
        self.assertAlmostEqual(R[2, 0], 0)
        self.assertAlmostEqual(R[2, 1], 0)
        self.assertAlmostEqual(R[2, 2], 1)
        
    def test_05_noRotation(self):
        alpha = 0
        q = Quaternion.from_v_theta((0, 0, 1), alpha)
        
        n_hat, alpha_hat = q.as_v_theta()
        
        self.assertEqual(alpha_hat, alpha)

        check = np.alltrue(np.isfinite(n_hat))
        self.assertTrue(check)

    def test_06_noRotation(self):
        alpha = 0
        n = np.array((1, 1, 1))
        q = Quaternion.from_v_v(n, n)
        
        n_hat, alpha_hat = q.as_v_theta()
        
        self.assertEqual(alpha_hat, alpha)
