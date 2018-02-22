"""
Tests for saving/loading sparse matrices to/from hdf5 files.
"""
import unittest
import h5py
import scipy.sparse as sp
from ..utils import *
import numpy as np
class TestSave(unittest.TestCase):

    def test_save_load_bsr(self):
        """BSR matrix"""
        M = sp.rand(n=20,m=20, format='bsr')

        with h5py.File('test.h5', 'w') as f:
            save_sparse_matrix(f, "mat", M)

        with h5py.File('test.h5', 'r') as f:
            M2 = load_sparse_matrix(f["mat"])

        self.assertEqual(M2.format, "bsr")
 
        np.testing.assert_allclose(M.A,M2.A)

    def test_save_load_coo(self):
        """COO matrix"""
        M = sp.rand(n=20,m=20, format='coo')

        with h5py.File('test.h5', 'w') as f:
            save_sparse_matrix(f, "mat", M)

        with h5py.File('test.h5', 'r') as f:
            M2 = load_sparse_matrix(f["mat"])

        self.assertEqual(M2.format, "coo")
 
        np.testing.assert_allclose(M.A,M2.A)

    def test_save_load_csc(self):
        """CSC matrix"""
        M = sp.rand(n=20,m=20, format='csc')

        with h5py.File('test.h5', 'w') as f:
            save_sparse_matrix(f, "mat", M)

        with h5py.File('test.h5', 'r') as f:
            M2 = load_sparse_matrix(f["mat"])

        self.assertEqual(M2.format, "csc")

        np.testing.assert_allclose(M.A,M2.A)

def test_save_load_csr(self):
        """CSR matrix"""
        M = sp.rand(n=20,m=20, format='csr')

        with h5py.File('test.h5', 'w') as f:
            save_sparse_matrix(f, "mat", M)

        with h5py.File('test.h5', 'r') as f:
            M2 = load_sparse_matrix(f["mat"])

        self.assertEqual(M2.format, "csr")

        np.testing.assert_allclose(M.A,M2.A)

def test_save_load_dia(self):
        """DIA matrix"""
        M = sp.rand(n=20,m=20, format='dia')

        with h5py.File('test.h5', 'w') as f:
            save_sparse_matrix(f, "mat", M)

        with h5py.File('test.h5', 'r') as f:
            M2 = load_sparse_matrix(f["mat"])

        self.assertEqual(M2.format, "dia")

        np.testing.assert_allclose(M.A,M2.A)

