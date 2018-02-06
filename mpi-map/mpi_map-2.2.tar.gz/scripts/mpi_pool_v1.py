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
    rank = MPI.COMM_WORLD.rank

    # Get cwd parameters
    (cwd, import_set) = comm.bcast(None, root=0)
    # print("Rank %d: mpi_pool.runner: broadcast #1" % rank)
    # Set cwd in the PYTHONPATH
    sys.path.append(cwd)
    # Import necessary modules
    for (module, as_field) in import_set:
        exec("import %s as %s" % (module, as_field))

    obj_gather = None
    distr_mem = {}
    STOP = False
    while not STOP:
        try:
            # Get next command from parent
            bcast_tuple_dill = comm.bcast(None, root=0)
            (obj_dill, f_in, obj_bcast, dmem_key_in_list, dmem_arg_in_list,
             dmem_key_out_list, red_obj_dill, import_set) = dill.loads(bcast_tuple_dill)
            # print("Rank %d: mpi_pool.runner: broadcast #2" % rank)

            # Check whether to stop
            if isinstance(obj_dill, str) and obj_dill == "STOP":
                STOP = True
            else:                
                # Get reduce arguments
                part_red_args = comm.scatter(None, root=0)
                # print("Rank %d: mpi_pool.runner: scatter #1" % rank)
                
                # Get scattered data
                obj_scatter = comm.scatter(None, root=0)
                # print("Rank %d: mpi_pool.runner: scatter #2" % rank)

                # Import necessary modules
                for (module, as_field) in import_set:
                    exec("import %s as %s" % (module, as_field))

                # Unpickle object
                obj = dill.loads(obj_dill)
                if obj is None:
                    func = dill.loads(f_in)
                elif isinstance(obj, str): # Retrieve object in distributed memory
                    func = getattr(distr_mem[obj], f_in)
                else:
                    try:
                        func = getattr(obj, f_in)
                    except AttributeError:
                        raise NotImplementedError("Class %s " % obj.__class__.__name__ + \
                                                  "does not implement method %s" % f_in)
                
                # Prepare input arguments
                tmp = {}
                tmp.update(obj_scatter)
                tmp.update(obj_bcast)
                for key, arg in zip(dmem_key_in_list, dmem_arg_in_list):
                    try:
                        tmp[arg] = distr_mem[key]
                    except KeyError:
                        distr_mem[key] = None
                        tmp[arg] = distr_mem[key]
                # Evaluate
                out = func(**tmp)
                # print("Rank %d: mpi_pool.runner: evaluate" % rank)
                # Split output in stuff to be gathered and stuff to be added to memory
                if len(dmem_key_out_list) == 0:
                    obj_gather = out
                else:
                    obj_gather = out[0]
                    for i,key in enumerate(dmem_key_out_list):
                        distr_mem[key] = out[i+1]

                # Unpickle reduce object
                reduce_obj = dill.loads(red_obj_dill)
                if reduce_obj is not None:
                    obj_gather = reduce_obj.inner_reduce(obj_gather, **part_red_args)
                # print("Rank %d: mpi_pool.runner: reduce" % rank)
            
        except Exception as e:
            obj_gather = (e, traceback.format_exc())
        finally:            
            # Gather
            comm.gather(obj_gather, root=0)
            # print("Rank %d: mpi_pool.runner: gather #2" % rank)

    # Reset PYTHONPATH
    sys.path.remove(cwd)

    # print("Rank %d: Disconnect [before]" % rank)
    # comm.Disconnect()
    # print("Rank %d: Disconnect [after]" % rank)
