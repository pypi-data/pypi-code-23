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
# Author: Daniele Bigoni
#

import sys, getopt
import logging
import numpy as np
import numpy.random as npr
import time
import traceback
import mpi_map
from mpi4py import MPI

mpi_map.logger.setLevel(logging.DEBUG)

def full_usage():
    print("Usage: python pool.py [-n <nprocs>]")

argv = sys.argv[1:]
NPROCS = 1
try:
    opts, args = getopt.getopt(argv,"hn:")
except getopt.GetoptError:
    full_usage()
    sys.exit(1)
for opt,arg in opts:
    if opt == '-h':
        full_usage()
        sys.exit()
    elif opt in ("-n"):
        NPROCS = int(arg)
    else:
        print("Error: Unrecognized input")
        full_usage()
        sys.exit(2)

class Operator(object):
    def dot(self, x, A):
        return np.dot(A,x.T).T

def set_A(A):
    return (None,A)

op = Operator()
A = npr.randn(5*5).reshape(5,5)
n = 2

import_set = set([("numpy","np")])
pool = mpi_map.MPI_Pool()
pool.start(NPROCS, import_set)
try:
    time.sleep(5)
    
    # Set params on nodes' memory
    params = {'A': A}
    pool.eval(set_A, obj_bcast=params,
              dmem_key_out_list=['A'])

    # Evaluate on firts input
    x = npr.randn(100,5)
    split = pool.split_data([x],['x'])
    xdot_list = pool.eval("dot", obj_scatter=split,
                          dmem_key_in_list=['A'], dmem_arg_in_list=['A'],
                          obj=op)
    xdot = np.concatenate(xdot_list, axis=0)

    # Evaluate on second input
    y = npr.randn(100,5)
    split = pool.split_data([y],['x'])
    ydot_list = pool.eval("dot", obj_scatter=split,
                          dmem_key_in_list=['A'], dmem_arg_in_list=['A'],
                          obj=op)
    ydot = np.concatenate(ydot_list, axis=0)
finally:
    pool.stop()

# Check whether dot is right
if not np.allclose(xdot, np.dot(A, x.T).T):
    print("First dot FAILED")
else:
    print("First dot SUCCESS")
if not np.allclose(ydot, np.dot(A, y.T).T):
    print("Second dot FAILED")
else:
    print("Second dot SUCCESS")

# # Check errors
# pool.start(NPROCS)
# try:
#     xfail = np.concatenate(pool.eval("sum", obj=op), axis=0)
# except:
#     print(traceback.format_exc())
#     print("Exception catched successfully")
# finally:
#     pool.stop()


