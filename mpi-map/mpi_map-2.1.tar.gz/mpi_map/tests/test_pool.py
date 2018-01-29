#
# This file is part of mpi_map.
#
# mpi_map is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mpi_map is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with mpi_map.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import unittest
import numpy as np
import numpy.random as npr

import mpi_map

class PoolTest(unittest.TestCase):

    def setUp(self):
        npr.seed(1)
        self.mpi_pool = mpi_map.MPI_Pool_v2()
        self.mpi_pool.start(2)
        self.mpi_pool.mod_import( set([ (None, 'numpy', 'np') ]) )

    def tearDown(self):
        self.mpi_pool.stop()

    def test_matrix_dot(self):
        # Test matrix vector product dot(A, X.T).T for a list of vectors.
        # The matrix A is broadcasted
        n = 10
        m = 100
        A = npr.randn(n, n)
        X = npr.randn(m, n)

        def dot(A, X):
            return np.dot(A, X.T).T

        # bcast arguments
        obj_bcast = {'A': A}
        # scatter arguments
        obj_scatter = self.mpi_pool.split_data( (X,), ('X',) )

        # Evaluate with MPI
        mpi_res = self.mpi_pool.map(
            dot, obj_scatter=obj_scatter, obj_bcast=obj_bcast)
        mpi_res = np.vstack( mpi_res )

        # Evaluate without MPI
        ser_res = dot(A, X)

        # Check all equal
        self.assertTrue( np.all(np.equal(mpi_res, ser_res)) )

    def test_matrix_dot_alloc_dmem(self):
        # Test matrix vector product dot(A, X.T).T for a list of vectors
        # The matrix A is first stored in memory, by memory allocation
        n = 10
        m = 100
        A = npr.randn(n, n)
        X = npr.randn(m, n)

        def dot(A, X):
            return np.dot(A, X.T).T

        # bcast A to distributed memory
        self.mpi_pool.alloc_dmem(A=A)

        # prepare scatter arguments
        obj_scatter = self.mpi_pool.split_data( (X,), ('X',) )

        # Evaluate with MPI
        dmem_key_in_list = ['A']
        dmem_arg_in_list = ['A']
        mpi_res = self.mpi_pool.map(
            dot, obj_scatter=obj_scatter,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list)
        mpi_res = np.vstack( mpi_res )

        # Evaluate without MPI
        ser_res = dot(A, X)

        # Check all equal
        self.assertTrue( np.all(np.equal(mpi_res, ser_res)) )

    def test_matrix_dot_map_alloc_dmem(self):
        # Test matrix vector product dot(A, X.T).T for a list of vectors
        # The matrix A is allocated locally by the subprocesses
        n = 10
        m = 100
        X = npr.randn(m, n)

        def alloc_A(n):
            npr.seed(1)
            A = npr.randn(n, n)
            return (A,)

        def dot(A, X):
            return np.dot(A, X.T).T

        # Import numpy.random on subprocesses
        import_set = set([ ('numpy', 'random', 'npr') ])
        self.mpi_pool.mod_import(import_set)
            
        # Allocate A in memory
        obj_bcast = {'n': n}
        dmem_key_out_list = ['A']
        self.mpi_pool.map_alloc_dmem(alloc_A, obj_bcast=obj_bcast,
                                     dmem_key_out_list=dmem_key_out_list)

        # Retrieve A
        mpi_A_list = self.mpi_pool.get_dmem('A')
        
        # prepare scatter arguments
        obj_scatter = self.mpi_pool.split_data( (X,), ('X',) )

        # Evaluate without MPI
        ser_res = [ dot(A[0], scttr['X']) for A, scttr in zip(mpi_A_list, obj_scatter) ]
        ser_res = np.vstack( ser_res )
        
        # Evaluate with MPI
        dmem_key_in_list = ['A']
        dmem_arg_in_list = ['A']
        mpi_res = self.mpi_pool.map(
            dot, obj_scatter=obj_scatter,
            dmem_key_in_list=dmem_key_in_list,
            dmem_arg_in_list=dmem_arg_in_list)
        mpi_res = np.vstack( mpi_res )

        # Check all equal
        self.assertTrue( np.all(np.equal(mpi_res, ser_res)) )

    def test_append_list_pop_dmem(self):
        a1 = npr.randn(10)
        a2 = npr.randn(10)
        a3 = npr.randn(10)

        # bcast a1, a2, a3 to distributed memory
        self.mpi_pool.alloc_dmem(a1=a1, a2=a2, a3=a3)

        # List objects in distributed memory
        dmem_list = self.mpi_pool.list_dmem()
        self.assertTrue( np.all( [
            set(['a1', 'a2', 'a3']) <= set(dmem) and \
            set(['a1', 'a2', 'a3']) >= set(dmem) \
            for dmem in dmem_list ] ) )

        # Pop a2
        a2_pop_list = self.mpi_pool.pop_dmem('a2')
        self.assertTrue( np.all( np.all( [
            np.equal(a2_pop, a2) for a2_pop in a2_pop_list ] ) ) )

        # List objects in distributed memory
        dmem_list = self.mpi_pool.list_dmem()
        self.assertTrue( np.all([
            set(['a1', 'a3']) <= set(dmem) and \
            set(['a1', 'a3']) >= set(dmem) \
            for dmem in dmem_list] ) )

def build_suite():
    suite_pool_test = unittest.TestLoader().loadTestsFromTestCase( PoolTest )
    # Group suites
    suites_list = [ suite_pool_test ]
    all_suites = unittest.TestSuite( suites_list )
    return all_suites

def run_tests():
    all_suites = build_suite()
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()