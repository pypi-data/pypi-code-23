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

if MPI.COMM_WORLD.rank == 0:

    class ExpectationReduce(mpi_map.ReduceObject):
        r""" Define the expectation operation carried out through the mpi_eval function
        """
        def __init__(self):
            self.axis = (0,0)
        def split_args(self, args, nprocs):
            args_split, ns = mpi_map.split_data(args, nprocs)
            return args_split
        def inner_reduce(self, x, args):
            return np.tensordot(x, args, self.axis)
        def outer_reduce(self, x, args):
            return sum( x )
    
    class Operator(object):
        def __init__(self, a):
            self.a = a
        def sum(self, x, n=1):
            out = x.copy()
            for i in range(n):
                out += self.a
            return out

    import_set = set([ ('numpy', 'np') ])
            
    N = 10
    op = Operator(2.)
    x = npr.randn(N,5)
    n = 2
    w = np.ones(N)/float(N)

    xsum = np.concatenate(mpi_map.eval_method("sum", x, (n,), op), axis=0)
    expected = np.tensordot(xsum, w, (0,0))
    
    reduce_obj = ExpectationReduce()
    reduced = mpi_map.eval_method("sum", x, (n,), op,
                                  reduce_obj=reduce_obj, reduce_args=w,
                                  import_set=import_set)

    if np.allclose(expected, reduced):
        print("Test PASSED")
    else:
        print("Test FAILED")