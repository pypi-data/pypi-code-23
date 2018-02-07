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

import sys
import os
import mpi_map
import dill
import traceback
import importlib
import logging
try:
    from mpi4py import MPI
    MPI_SUPPORT = True
except ImportError:
    MPI_SUPPORT = False

def binary_bcast(comm, logger):
    logger.debug("Rank: %d - binary bcast #1" % rank)
    tot_size = comm.bcast(None, root=0)
    obj = bytearray(tot_size)
    continue_flag = True
    idx = 0
    while continue_flag:
        logger.debug("Rank: %d - binary bcast #2" % rank)
        comm.Barrier()
        logger.debug("Rank: %d - binary bcast #3" % rank)
        buf_size = comm.bcast(None, root=0)
        if 'bffr' not in locals() or len(bffr) != buf_size:
            bffr = bytearray(buf_size)
        # Get data
        logger.debug("Rank: %d - binary bcast #4" % rank)
        comm.Bcast(bffr, root=0)
        # Write data on output object
        obj[idx:idx+buf_size] = bffr[:]
        idx += buf_size
        # Get continuation flag
        logger.debug("Rank: %d - binary bcast #5" % rank)
        continue_flag = comm.bcast(None, root=0)
    obj = dill.loads(obj)
    return obj

def binary_scatter(comm, logger):
    logger.debug("Rank: %d - binary scatter #1" % rank)
    tot_size = comm.scatter(None, root=0)
    obj = bytearray(tot_size)
    continue_flag = True
    idx = 0
    while continue_flag:
        logger.debug("Rank: %d - binary scatter #2" % rank)
        comm.Barrier()
        logger.debug("Rank: %d - binary scatter #3" % rank)
        buf_size = comm.bcast(None, root=0)
        logger.debug("Rank: %d - binary scatter #4" % rank)
        msg_size = comm.scatter(None, root=0)
        if 'bffr' not in locals() or len(bffr) != buf_size:
            bffr = bytearray(buf_size)
        # Get the data
        logger.debug("Rank: %d - binary scatter #5" % rank)
        comm.Scatter(None, bffr, root=0)
        # Write data on output object
        obj[idx:idx+msg_size] = bffr[:msg_size]
        idx += msg_size
        # Get continuation flag
        logger.debug("Rank: %d - binary scatter #6" % rank)
        continue_flag = comm.bcast(None, root=0)
    obj = dill.loads(obj)
    return obj

def binary_gather(obj_gather, comm, maxbchunk, logger):
    obj_gather = dill.dumps(obj_gather)
    logger.debug("Rank: %d - binary gather #1" % rank)
    comm.gather( len(obj_gather), root=0 )
    continue_flag = True
    start = 0
    while continue_flag:
        logger.debug("Rank: %d - binary gather #2" % rank)
        comm.Barrier()
        # gather chunk size
        stop = min(start+maxbchunk, len(obj_gather))
        logger.debug("Rank: %d - binary gather #3" % rank)
        msg_size = stop-start
        comm.gather( msg_size, root=0 )
        # get buffer size
        logger.debug("Rank: %d - binary gather #4" % rank)
        buf_size = comm.bcast(None, root=0)
        chunk = bytearray(buf_size)
        chunk[:msg_size] = obj_gather[start:stop]
        # gather chunk
        logger.debug("Rank: %d - binary gather #5" % rank)
        comm.Gather( chunk, None, root=0 )
        # get stopping flag
        logger.debug("Rank: %d - binary gather #6" % rank)
        continue_flag = comm.bcast(None, root=0)
        start = stop
    
if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    comm = MPI.Comm.Get_parent()
    rank = MPI.COMM_WORLD.rank
    world_size = MPI.COMM_WORLD.size
    logger = logging.getLogger("mpi_pool_v2")
    logger.propagate = False
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(name)s: %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    comm.Barrier()
    
    # Get cwd parameters
    cwd, maxbchunk, log_level = comm.bcast(None, root=0)
    logger.setLevel(log_level)
    logger.debug("Rank: %d - Size: %d" % (rank, world_size))
    logger.debug("Rank: %d - cwd: %s" % (rank, cwd))
    # Set cwd in the PYTHONPATH
    sys.path.append(cwd)

    obj_gather = None
    distr_mem = {}
    # import_dict = {}
    STOP = False
    while not STOP:
        try:
            # Get next command from parent
            logger.debug("Rank: %d - Barrier" % rank)
            comm.Barrier()

            cmd_tuple = binary_bcast(comm, logger)
            cmd_str = cmd_tuple[0]
            logger.info("Rank: %d - Command: %s" % (rank, cmd_str))
            
            if cmd_str == "STOP": # Terminates
                STOP = True
                obj_gather = None
                
            elif cmd_str == "IMPORT": # Import command
                import_set = cmd_tuple[1]
                for (frm, module, as_field) in import_set:
                    # import_dict[as_field] = importlib.import_module(module, frm)
                    exec_str = "from %s " % frm if frm is not None else ""
                    exec_str += "import %s " % module
                    exec_str += "as %s" % as_field
                    exec(exec_str)
                obj_gather = None

            elif cmd_str == "SET_LOG_LEVEL": # Set logging level
                log_level = cmd_tuple[1]
                logger.setLevel(log_level)
                obj_gather = None
                
            elif cmd_str in ("MAP", "MAP_ALLOC_DMEM"): # Map-reduce command
                if cmd_str == "MAP":
                    (obj, f, obj_bcast,
                     dmem_key_in_list, dmem_arg_in_list,
                     reduce_obj) = cmd_tuple[1:]
                else:
                    (obj, f, obj_bcast,
                     dmem_key_in_list, dmem_arg_in_list,
                     dmem_key_out_list, reduce_obj) = cmd_tuple[1:]
                
                # Get reduce arguments
                logger.debug("Rank: %d - MAP/MAP_ALLOC_DMEM scatter #1" % rank)
                part_red_args = binary_scatter(comm, logger)
                
                # Get scattered data
                logger.debug("Rank: %d - MAP/MAP_ALLOC_DMEM scatter #2" % rank)
                obj_scatter = binary_scatter(comm, logger)
                
                # Unpickle object
                if obj is None:
                    func = f
                elif isinstance(obj, str): # Retrieve object in distributed memory
                    func = getattr(distr_mem[obj], f)
                else:
                    try:
                        func = getattr(obj, f)
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
                logger.debug("Rank: %d - MAP/MAP_ALLOC_DMEM Evaluate" % rank)
                out = func(**tmp)
                logger.debug("Rank: %d - MAP/MAP_ALLOC_DMEM Evaluate [DONE]" % rank)

                # Unpickle reduce object
                if reduce_obj is not None:
                    logger.debug("Rank: %d - MAP/MAP_ALLOC_DMEM Reduce" % rank)
                    out = reduce_obj.inner_reduce(out, **part_red_args)

                if cmd_str == "MAP":
                    obj_gather = out
                else:
                    obj_gather = None
                    for i, key in enumerate(dmem_key_out_list):
                        distr_mem[key] = out[i]
                        
            elif cmd_str == "ALLOC_DMEM":
                kwargs = cmd_tuple[1]
                distr_mem.update(kwargs)
                obj_gather = None
                
            elif cmd_str == "GET_DMEM":
                dmem_key_in_list = cmd_tuple[1]
                obj_gather = tuple([
                    distr_mem[key] for key in dmem_key_in_list ])
                
            elif cmd_str == "POP_DMEM":
                dmem_key_in_list = cmd_tuple[1]
                obj_gather = tuple([
                    distr_mem.pop(key) for key in dmem_key_in_list ])
                
            elif cmd_str == "LIST_DMEM":
                obj_gather = tuple([ key for key in distr_mem ])
                
            elif cmd_str == "CLEAR_DMEM":
                distr_mem.clear()
                obj_gather = None
                
        except Exception as e:
            obj_gather = (e, traceback.format_exc())
        finally:            
            # Gather
            binary_gather(obj_gather, comm, maxbchunk, logger)

    # Reset PYTHONPATH
    sys.path.remove(cwd)

    # print("Rank %d: Disconnect [before]" % rank)
    # comm.Disconnect()
    # print("Rank %d: Disconnect [after]" % rank)
