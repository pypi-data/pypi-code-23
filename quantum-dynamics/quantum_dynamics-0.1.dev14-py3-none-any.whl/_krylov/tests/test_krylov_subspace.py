#!/usr/bin/env python3

"""
Tests for the Krylov Subspace class.
"""

import numpy as np
import unittest
from .._krylov_subspace import *


class TestKrylovSubspace(unittest.TestCase):

    def test_shapes(self):
        """Testing matrix dimensions we get from the arnoldi iteration."""
        A = np.random.random((10, 10))

        v = np.random.random(10)

        KS = KrylovSubspace(A, v)

        KS.grow()

        V, H = KS.get()

        self.assertEqual(V.shape[0], A.shape[0])
        self.assertEqual(V.shape[1], 2)

    def test_arnoldi_single_iteration(self):
        """Test single iteration of the Arnoldi process"""
        A = np.arange(0.0, 9.0, 1.0).reshape((3, 3))
        v = np.array([1, 2, 3])
        KS = KrylovSubspace(A, v)
        KS.grow()
        V, H = KS.get()

        # Check initial vector norm
        self.assertAlmostEqual(KS.β, np.sqrt(14))

        # Check the projected operator
        self.assertAlmostEqual(H[0, 0], 96 / 7)
        self.assertAlmostEqual(H[1, 0], 5 * np.sqrt(6) / 7)

        # Check the projection matrix
        v0_exact = np.array([1, 2, 3]) / np.sqrt(14)
        v1_exact = np.array([-4, -1, 2]) / np.sqrt(21)

        np.testing.assert_almost_equal(V[:, 0], v0_exact)
        np.testing.assert_almost_equal(V[:, 1], v1_exact)

    def test_continue_arnoldi(self):
        """Test continuing the Arnoldi process"""
        A = np.random.random((15, 15))
        v = np.random.random(A.shape[0])
        KS = KrylovSubspace(A, v)
        KS.grow()
        V1, H1 = KS.get()
        KS.grow()

        # We get already invariant subspace
        self.assertFalse(KS.invariant)
        self.assertEqual(KS.dim, 2)

        V, H = KS.get()

        # Check that the previous step(s) is(are) included correctly
        np.testing.assert_almost_equal(V[:, :-1], V1)
        np.testing.assert_almost_equal(H[:2, :2], H1)

    def test_invariant_space(self):
        A = np.arange(0.0, 9.0, 1.0).reshape((3, 3))
        v = np.array([1, 2, 3])
        KS = KrylovSubspace(A, v)
        KS.grow()
        KS.grow()
        V, H = KS.get()
        self.assertTrue(KS.invariant)
        self.assertEqual(V.shape[1], 2)
