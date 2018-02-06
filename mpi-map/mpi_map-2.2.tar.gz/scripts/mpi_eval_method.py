#!/usr/bin/env python

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

__all__ = []

import sys, os, mpi_map, dill, traceback
try:
    from mpi4py import MPI
    MPI_SUPPORT = True
except ImportError:
    MPI_SUPPORT = False
    
if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    
    comm = MPI.Comm.Get_parent()

    try:
        # Get the broadcasted function and parameters
        comm.Barrier()
        (cwd, obj_dill, fname, params, red_obj_dill, import_set) = comm.bcast(None, root=0)

        # Set cwd in the PYTHONPATH
        sys.path.append(cwd)

        # Import necessary modules
        for (module, as_field) in import_set:
            exec("import %s as %s" % (module, as_field))
        
        # Unpickle object
        obj = dill.loads(obj_dill)

        # Unpickle reduce object
        reduce_obj = dill.loads(red_obj_dill)

        # Get reduce arguments
        comm.Barrier()
        part_red_args = comm.scatter(None, root=0)
        
        # Get scattered data
        comm.Barrier()
        part_x = comm.scatter(None, root=0)

        # Get method
        if obj is not None and isinstance(f, str):
            func = None
            try:
                func = getattr(obj, fname)
            except AttributeError:
                raise NotImplementedError("Class %s " % obj.__class__.__name__ + \
                                          "does not implement method %s" % fname)
        else:
            func = f
                
        # Evaluate
        if isinstance(part_x, list):
            fval = [ func(x, *params) for x in part_x ]
        else:
            fval = func(part_x, *params)

        # Reduce
        if reduce_obj is not None:
            fval = reduce_obj.inner_reduce(fval, part_red_args)

    except Exception as e:
        fval = (e, traceback.format_exc())
    else:
        # Reset PYTHONPATH
        sys.path.remove(cwd)
    finally:
        # Gather
        comm.Barrier()
        comm.gather(fval, root=0)

    comm.Barrier()
    # comm.Disconnect()
