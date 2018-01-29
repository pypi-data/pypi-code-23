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

import logging
import numpy as np
import numpy.random as npr
import traceback
import mpi_map
from mpi4py import MPI

mpi_map.logger.setLevel(logging.DEBUG)

class ExpectationReduce(mpi_map.ReduceObject):
    r""" Define the expectation operation carried out through the mpi_eval function
    """
    def __init__(self):
        self.axis = (0,0)
    def inner_reduce(self, x, w):
        return np.tensordot(x, w, self.axis)
    def outer_reduce(self, x, *args, **kwargs):
        return sum( x )

class Operator(object):
    def __init__(self):
        pass
    def dot(self, x, A):
        return np.dot(A,x.T).T

def set_A(A):
    return (None,A)
        
nprocs = 4

import_set = set([ ('numpy', 'np') ])

op = Operator()
N = 1000
x = npr.randn(N,5)
w = np.ones(N)/float(N)
A = npr.randn(5*5).reshape(5,5)

pool = mpi_map.MPI_Pool()
pool.start(nprocs, import_set)
try:
    # Set params on nodes' memory
    params = {'A': A}
    pool.eval(set_A, obj_bcast=params,
              dmem_key_out_list=['A'])

    # Evaluate
    split = pool.split_data([x], ['x'])
    xdot_list = pool.eval("dot", obj_scatter=split,
                          dmem_key_in_list=['A'], dmem_arg_in_list=['A'],
                          obj=op)
    xdot = np.concatenate(xdot_list, axis=0)
    expected = np.tensordot(xdot, w, (0,0))
finally:
    pool.stop()

reduce_obj = ExpectationReduce()
pool.start(nprocs, import_set)
try:
    # Set params on nodes' memory
    params = {'A': A}
    pool.eval(set_A, obj_bcast=params,
              dmem_key_out_list=['A'])

    # Split scattering input
    split = pool.split_data([x], ['x'])
    split_args = pool.split_data([w], ['w'])

    # Evaluate
    reduced = pool.eval("dot", obj_scatter=split, dmem_key_in_list=['A'],
                        dmem_arg_in_list=['A'], obj=op,
                        reduce_obj=reduce_obj, reduce_args=split_args)
finally:
    pool.stop()

if np.allclose(expected, reduced):
    print("Test PASSED")
else:
    print("Test FAILED")
