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

    class Operator(object):
        def __init__(self, a):
            self.a = a
        def sum(self, x, n=1):
            out = x
            for i in range(n):
                out += self.a
            return out
        def mul(self, x, n=1):
            out = x
            for i in range(n):
                out *= self.a
            return out

    op = Operator(2.)
    x = npr.randn(10,5)
    n = 2

    xsum = np.concatenate(mpi_map.eval_method("sum", x, (n,), op), axis=0)
    xmul = np.concatenate(mpi_map.eval_method("mul", x, (n,), op), axis=0)

    try:
        xfail = np.concatenate(mpi_map.eval_method("sum", None, (n,), op), axis=0)
    except:
        print(traceback.format_exc())
        print("Exception catched successfully")
    

