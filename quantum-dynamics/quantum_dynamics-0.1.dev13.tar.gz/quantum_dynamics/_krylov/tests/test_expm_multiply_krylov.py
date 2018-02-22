#!/usr/bin/env python3

import unittest
from ..exponential import *

import numpy as np
import scipy.linalg as la
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from ..type_checking import *


class TestKrylovExponential(unittest.TestCase):

    """Tests for the Krylov subspace based matrix exponential"""

    def test_small(self):
        """Testing Arnoldi-based expm_multiply with small dense matrices"""
        for i in range(20):
            N = 10
            A = np.random.random((N, N))
            v = np.random.random(N)

            # Our implementation
            w = expm_multiply(A, v, rtol=1e-6)

            # Reference result
            w_pade = la.expm(A)@v

            np.testing.assert_allclose(w, w_pade, atol=0, rtol=1e-4)

    def test_medium_sparse(self):
        """Testing Arnoldi-based expm_multiply with larger dense matrices"""
        for i in range(5):
            N = 100
            A = sp.rand(N, N)
            v = np.random.random(N)

            w = expm_multiply(A, v, rtol=1e-6)

            # Reference result
            w_pade = sla.expm_multiply(A, v)

            np.testing.assert_allclose(w, w_pade, atol=0, rtol=1e-4)

    def test_large_extra_sparse(self):
        """Testing Arnoldi-based expm_multiply with large sparse matrices"""
        for i in range(10):
            N = 5000
            A = sp.rand(N, N, density=0.00005)
            v = np.random.random(N)

            w = expm_multiply(A, v, rtol=1e-7)

            # Use pade approximant as reference
            w_pade = sla.expm_multiply(A, v)

        np.testing.assert_allclose(w, w_pade, atol=0, rtol=1e-4)

    def test_timestep(self):
        """Testing timestep in the Arnoldi-based expm_multiply"""
        for i in range(10):
            N = 5000
            A = sp.rand(N, N, density=0.0001)
            v = np.random.random(N)

            w = expm_multiply(A, v, t=0.5j, rtol=1e-6)

            # Use pade approximant as reference
            w_pade = sla.expm_multiply(0.5j * A, v)

            np.testing.assert_allclose(w, w_pade, atol=0, rtol=1e-4)

    def test_wrong_type_A(self):
        """Test preconditions for A"""

        with self.assertRaises((TypeError, AssertionError)):
            A = "AAA"
            v = np.random.random(3)
            w = expm_multiply(A, v)

        with self.assertRaises((TypeError, AssertionError)):
            A = np.eye(N=4, M=3)
            v = np.random.random(3)
            w = expm_multiply(A, v)

        with self.assertRaises((TypeError, AssertionError)):
            A = np.eye(N=3, M=3)
            v = np.random.random(4)
            w = expm_multiply(A, v)

        with self.assertRaises((TypeError, AssertionError)):
            A = np.eye(N=3, M=3)
            v = np.random.random((3, 3))
            w = expm_multiply(A, v)

        with self.assertRaises((TypeError, AssertionError)):
            A = np.eye(N=3, M=3)
            v = np.random.random((1, 3))
            w = expm_multiply(A, v)

    def test_output_types(self):
        """If all input is real, output is real"""
        A = np.eye(N=3, M=3)
        v = np.random.random(3)
        w = expm_multiply(A, v)

        self.assertTrue(is_numpy_array_of_reals(w))
    
    def test_mixed_input_types(self):
        """If some input is complex, output is complex"""
        A = np.eye(N=3, M=3, dtype=np.complex)
        v = np.random.random(3)
        w = expm_multiply(A,v)

        self.assertEqual(w.dtype, np.dtype('complex'))
        np.testing.assert_allclose(w, la.expm(A)@v)

        A = np.eye(N=3, M=3, dtype=np.float)
        v = np.random.random(3)+np.random.random(3)*1j
        w = expm_multiply(A,v)

        self.assertEqual(w.dtype, np.dtype('complex'))
        np.testing.assert_allclose(w, la.expm(A)@v)

        A = np.eye(N=3, M=3, dtype=np.complex)
        v = np.random.random(3)+np.random.random(3)*1j
        w = expm_multiply(A,v)

        self.assertEqual(w.dtype, np.dtype('complex'))
        np.testing.assert_allclose(w, la.expm(A)@v)

    def test_mixed_input_types(self):
        """If some input is complex, output is complex"""
        A = np.eye(N=3, M=3, dtype=np.complex)
        v = np.random.random(3)
        w = expm_multiply(A, v)

        self.assertEqual(w.dtype, np.dtype('complex'))
        np.testing.assert_allclose(w, la.expm(A)@v)

        A = np.eye(N=3, M=3, dtype=np.float)
        v = np.random.random(3) + np.random.random(3) * 1j
        w = expm_multiply(A, v)

        self.assertEqual(w.dtype, np.dtype('complex'))
        np.testing.assert_allclose(w, la.expm(A)@v)

        A = np.eye(N=3, M=3, dtype=np.complex)
        v = np.random.random(3) + np.random.random(3) * 1j
        w = expm_multiply(A, v)

        self.assertEqual(w.dtype, np.dtype('complex'))
        np.testing.assert_allclose(w, la.expm(A)@v)

    def test_column_vector(self):
        """If input is a column vector then output is also a column vector"""
        A = np.eye(N=3, M=3)
        v = np.random.random((3, 1))
        w = expm_multiply(A, v)
        self.assertEqual(len(w.shape), 2)
        self.assertEqual(w.shape[0], 3)
        self.assertEqual(w.shape[1], 1)
