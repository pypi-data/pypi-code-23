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

__all__ = ['logger', 'get_avail_procs', 'split_data', 'mpi_map_code',
           'eval_method', 'barrier',
           'MPI_Pool_v2',
           'MPI_Pool_v1', 'MPI_Pool',
           'ReduceObject']

import os
import sys
import time
import marshal, types
import dill
import logging
import inspect
import itertools
import distutils.spawn
from mpi4py import MPI
import mpi_map

logger = logging.getLogger('mpi_map')
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

def get_avail_procs():
    return MPI.COMM_WORLD.Get_size()

def split_data(x, procs):
    # Split the input data
    ns = [len(x) // procs]*procs
    for i in range(len(x) % procs): ns[i] += 1
    for i in range(1,procs): ns[i] += ns[i-1]
    ns.insert(0,0)
    split_x = [ x[ns[i]:ns[i+1]] for i in range(0, procs) ]
    return (split_x, ns)

def mpi_map_code(f, x, params, procs, obj_dill=None):
    """ This function applies the function in ``func_code`` to the ``x`` inputs on ``procs`` processors.

    Args:
      f (function): function
      x (:class:`list` or :class:`ndarray<numpy.ndarray>`): input
      params (tuple): parameters to be passed to the function (pickable)
      procs (int): number of processors to be used
      obj (object): object where ``f``

    Returns:
      (:class:`list` [``nprocs``]) -- (ordered) outputs from all the processes
    """
    sys.setrecursionlimit(10000)
    func_code = marshal.dumps(f.__code__)
    if not obj is None:
        obj_dill = dill.dumps(obj)
    else: obj_dill = None
    
    try:
        path = os.environ['VIRTUAL_ENV'] + '/bin/mpi_eval.py'
    except KeyError:
        path = distutils.spawn.find_executable('mpi_eval.py')

    if len(x) > 0:
        cwd = os.getcwd()
        procs = min(procs,len(x))

        comm = MPI.COMM_SELF.Spawn(sys.executable,
                                   args=[path],
                                   maxprocs=procs)

        # Broadcast function and parameters
        comm.bcast((cwd, obj_dill, func_code, params), root=MPI.ROOT)

        # Split the input data
        split_x, ns = split_data(x, procs)

        # Scatter the data
        comm.scatter(split_x, root=MPI.ROOT)

        # # Avoid busy waiting
        # mpi_map.barrier(MPI.COMM_WORLD)

        # Gather the results
        fval = comm.gather(None,root=MPI.ROOT)

        comm.Free()
        # comm.Disconnect()

        # Check for exceptions
        for v in fval:
            fail = False
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            raise RuntimeError("Some of the MPI processes failed")

        if isinstance(fval[0], list):
            fval = list(itertools.chain(*fval))

    else:
        fval = []
    
    return fval

def eval_method(fname, x, params, obj, nprocs=None,
                reduce_obj=None, reduce_args=None,
                import_set=set(), splitted=False):
    """ This function applies the method with name ``fname`` of object ``obj`` to the ``x`` inputs on ``nprocs`` processors.

    Args:
      fname (str): name of the function defined in ``obj``
      x (:class:`list` or :class:`ndarray<numpy.ndarray>`): input
      params (tuple): parameters to be passed to the function (pickable)
      obj (object): object where ``f`` is defined
      nprocs (int): number of processes. If ``None`` then ``MPI.COMM_WORLD.Get_size()``
        processes will be started
      reduce_obj (object): object :class:`ReduceObject` defining the reduce
        method to be applied (if any)
      reduce_args (object): arguments to be provided to ``reduce_object``
      import_set (set): list of couples ``(module_name,as_field)`` to be imported
        as ``import module_name as as_field``
      splitted (bool): whether the input is already splitted

    Returns:
      (:class:`list` [``nprocs``]) -- (ordered) outputs from all the processes
    """
    
    sys.setrecursionlimit(10000)
    obj_dill = dill.dumps(obj)
    red_obj_dill = dill.dumps(reduce_obj)
    
    try:
        path = os.environ['VIRTUAL_ENV'] + '/bin/mpi_eval_method.py'
    except KeyError:
        path = distutils.spawn.find_executable('mpi_eval_method.py')

    if len(x) > 0:
        cwd = os.getcwd()

        if nprocs == None:
            nprocs = get_avail_procs()
        nprocs = min(nprocs,len(x))
        comm = MPI.COMM_SELF.Spawn(sys.executable,
                                   args=[path],
                                   maxprocs=nprocs)

        # Broadcast function and parameters
        comm.Barrier()
        comm.bcast((cwd, obj_dill, fname, params, red_obj_dill, import_set), root=MPI.ROOT)
        logger.debug("eval_method: broadcast")
        
        # Split the input data
        if splitted:
            if len(x) != nprocs:
                raise ValueError("The splitted input is not consistent with " + \
                                 "the number of processes")
            split_x = x
        else:
            split_x, ns = split_data(x, nprocs)

        # Split the reduce_args data
        if reduce_args is not None:
            if splitted:
                if len(reduce_args) != nprocs:
                    raise ValueError("The splitted reduce_args is not consistent with " + \
                                     "the number of processes")
                split_red_args = reduce_args
            else:
                split_red_args = reduce_obj.split_args(reduce_args, nprocs)
        else:
            split_red_args = [None for i in range(nprocs)]

        # Scatter reduce arguments
        comm.Barrier()
        comm.scatter(split_red_args, root=MPI.ROOT)
        logger.debug("eval_method: scatter")    
        
        # Scatter the data
        comm.Barrier()
        comm.scatter(split_x, root=MPI.ROOT)
        logger.debug("eval_method: scatter")

        # # Avoid busy waiting
        # mpi_map.barrier(MPI.COMM_WORLD)

        # Gather the results
        comm.Barrier()
        fval = comm.gather(None,root=MPI.ROOT)
        logger.debug("eval_method: gather")

        # Check for exceptions
        for v in fval:
            fail = False
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            raise RuntimeError("Some of the MPI processes failed")

        if reduce_obj is None and isinstance(fval[0], list):
            fval = list(itertools.chain(*fval))

    else:
        fval = []

    if reduce_obj is not None:
        fval = reduce_obj.outer_reduce(fval, reduce_args)

    comm.Barrier()
    # comm.Disconnect()
    comm.Free()
        
    return fval
    
def barrier(comm, tag=0, sleep=0.01):
    """ Function used to avoid busy-waiting.

    As suggested by Lisandro Dalcin at:
    * http://code.google.com/p/mpi4py/issues/detail?id=4 and
    * https://groups.google.com/forum/?fromgroups=#!topic/mpi4py/nArVuMXyyZI
    """
    size = comm.Get_size()
    if size == 1:
        return
    rank = comm.Get_rank()
    mask = 1
    while mask < size:
        dst = (rank + mask) % size
        src = (rank - mask + size) % size
        req = comm.isend(None, dst, tag)
        while not comm.Iprobe(src, tag):
            time.sleep(sleep)
        comm.recv(None, src, tag)
        req.Wait()
        mask <<= 1
    logger.debug("Mask %d, Size %d" % (mask, size))

class MPI_Pool_v2(object):
    r""" Returns (but not start) a pool of ``nprocs`` processes

    This implementation allows for a more flexible access to the distributed memory.
    The usage is similar to the one introduced in :class:`MPI_Pool_v1`.
    The following two examples are equivalent, but they modify the memory
    in two different ways.

    .. code-block:: python
    
        import numpy as np
        import numpy.random as npr
        import mpi_map

        class Operator(object):
            def dot(self, x, A):
                return np.dot(A,x.T).T

        def set_A(A):
            return (A,)

        nprocs = 2
        op = Operator()
        A = npr.randn(5*5).reshape(5,5)

        import_set = set([("numpy","np")])
        pool = mpi_map.MPI_Pool()
        pool.start(nprocs, import_set)
        try:
            # Set params on nodes' memory
            params = {'A': A}
            pool.map_alloc_dmem(set_A, obj_bcast=params,
                                dmem_key_out_list=['A'])

            # Evaluate on firts input
            x = npr.randn(100,5)
            split = pool.split_data([x],['x'])
            xdot_list = pool.map("dot", obj_scatter=split,
                                 dmem_key_in_list=['A'], dmem_arg_in_list=['A'],
                                 obj=op)
            xdot = np.concatenate(xdot_list, axis=0)

            # Evaluate on second input
            y = npr.randn(100,5)
            split = pool.split_data([y],['x'])
            ydot_list = pool.map("dot", obj_scatter=split,
                                 dmem_key_in_list=['A'], dmem_arg_in_list=['A'],
                                 obj=op)
            ydot = np.concatenate(ydot_list, axis=0)
        finally:
            pool.stop()

    .. code-block:: python
    
        import numpy as np
        import numpy.random as npr
        import mpi_map

        class Operator(object):
            def dot(self, x, A):
                return np.dot(A,x.T).T

        nprocs = 2
        op = Operator()
        A = npr.randn(5*5).reshape(5,5)

        import_set = set([("numpy","np")])
        pool = mpi_map.MPI_Pool()
        pool.start(nprocs, import_set)
        try:
            # Set params on nodes' memory
            pool.alloc_dmem(A=A)

            # Evaluate on firts input
            x = npr.randn(100,5)
            split = pool.split_data([x],['x'])
            xdot_list = pool.map("dot", obj_scatter=split,
                                 dmem_key_in_list=['A'], dmem_arg_in_list=['A'],
                                 obj=op)
            xdot = np.concatenate(xdot_list, axis=0)

            # Evaluate on second input
            y = npr.randn(100,5)
            split = pool.split_data([y],['x'])
            ydot_list = pool.map("dot", obj_scatter=split,
                                 dmem_key_in_list=['A'], dmem_arg_in_list=['A'],
                                 obj=op)
            ydot = np.concatenate(ydot_list, axis=0)
        finally:
            pool.stop()
    """
    
    def __init__(self):
        self.mpirun = False
        self.nprocs = None
        self.comm = None
        self.max_binary_chunk = None
        self._set_logger()

    def _set_logger(self):
        self.logger = logging.getLogger("mpi_map." + self.__class__.__name__)
        # self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        if len(self.logger.handlers) == 0:
            self.logger.propagate = False
            ch = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s %(levelname)s: %(name)s: %(message)s",
                                          "%Y-%m-%d %H:%M:%S")
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def _binary_bcast(self, bstream):
        # Serialize data
        bstream = dill.dumps(bstream)
        # Broadcast total length
        self.logger.debug("bcast #1")
        self.comm.bcast( len(bstream), root=MPI.ROOT )
        start = 0
        continue_flag = True
        while continue_flag:
            self.logger.debug("bcast #2")
            self.comm.Barrier()
            stop = min(start+self.max_binary_chunk, len(bstream))
            self.logger.debug("bcast #3")
            self.comm.bcast( stop-start, root=MPI.ROOT )
            # Broadcast data
            self.logger.debug("bcast #4")
            self.comm.Bcast( bstream[start:stop], root=MPI.ROOT )
            # Check whether to continue
            continue_flag = stop < len(bstream)
            self.logger.debug("bcast #5")
            self.comm.bcast( continue_flag, root=MPI.ROOT )
            # Update start
            start = stop

    def _binary_scatter(self, sstream_list):
        # Serialize data
        sstream_list = [ dill.dumps(obj) for obj in sstream_list ]
        # Scatter total lengths
        tot_size_list = [ len(sstream) for sstream in sstream_list ]
        self.logger.debug("scatter #1")
        self.comm.scatter( tot_size_list[:], root=MPI.ROOT )
        start_list = [ 0 for i in range(len(sstream_list)) ]
        continue_flag = True
        while continue_flag:
            self.logger.debug("scatter #2")
            self.comm.Barrier()
            # Prepare buffers
            stop_list = [ min(start+self.max_binary_chunk, len(sstream))
                          for start, sstream in zip(start_list, sstream_list) ]
            msg_size_list = [ stop - start for start, stop in zip(start_list, stop_list) ]
            buf_size = max(msg_size_list)
            if 'bffr' not in locals() or len(bffr) != buf_size * self.nprocs:
                bffr = bytearray( buf_size * self.nprocs )
            idx = 0
            for start, stop, sstream, msg_size in zip(
                    start_list, stop_list, sstream_list, msg_size_list):
                bffr[idx:idx+msg_size] = sstream[start:stop]
                idx += buf_size
            # Scatter size of different buffers
            self.logger.debug("scatter #3")
            self.comm.bcast( buf_size, root=MPI.ROOT)
            self.logger.debug("scatter #4")
            self.comm.scatter( msg_size_list, root=MPI.ROOT )
            # Scatter chunks of data
            self.logger.debug("scatter #5")
            self.comm.Scatter( bffr, None, root=MPI.ROOT )
            # Check whether to continue
            continue_flag = any([ stop < tot_size
                                  for stop, tot_size
                                  in zip(stop_list, tot_size_list) ])
            self.logger.debug("scatter #6")
            self.comm.bcast(continue_flag, root=MPI.ROOT)
            # Update start
            start_list = stop_list

    def _binary_gather(self):
        # Get total size from each node
        self.logger.debug("gather #1")
        tot_size_list = self.comm.gather(None, root=MPI.ROOT)
        fval_list = [ bytearray(tot_size) for tot_size in tot_size_list ]
        stop_list = [ 0 for i in range(self.nprocs) ]
        continue_flag = any([ stop < tot_size
                              for stop, tot_size
                              in zip(stop_list, tot_size_list) ])
        while continue_flag:
            self.logger.debug("gather #2")
            self.comm.Barrier()
            # Update start_list
            start_list = stop_list[:]
            # Update stop_list
            self.logger.debug("gather #3")
            msg_size_list = self.comm.gather(None, root=MPI.ROOT)
            stop_list = [ stop + msg_size
                          for stop, msg_size in zip(stop_list, msg_size_list) ]
            # Broadcast buffer size
            buf_size = max(msg_size_list)
            self.logger.debug("gather #4")
            self.comm.bcast(buf_size, root=MPI.ROOT)
            # Gather into one unique buffer
            bffr = bytearray( buf_size * self.nprocs )
            self.logger.debug("gather #5")
            self.comm.Gather(None, bffr, root=MPI.ROOT)
            # Split the buffer
            idx = 0
            for fval, start, stop, msg_size in zip(
                    fval_list, start_list, stop_list, msg_size_list):
                fval[start:stop] = bffr[idx:idx+msg_size]
                idx += buf_size
            # Check whether to continue
            continue_flag = any([ stop < tot_size
                                  for stop, tot_size
                                  in zip(stop_list, tot_size_list) ])
            self.logger.debug("gather #6")
            self.comm.bcast(continue_flag, root=MPI.ROOT)
        # De-serialize all the gathered objects
        for i in range(self.nprocs):
            fval_list[i] = dill.loads(fval_list[i])
        return fval_list
        
    def start(self, nprocs=None,
              max_binary_chunk=2**16-100,
              log_level=logging.WARNING):
        r""" Start the pool of processes

        Args:
          nprocs (int): number of processes. If ``None`` then ``MPI.COMM_WORLD.Get_size()``
            processes will be started
          max_binary_chunk (int): maximum byte size of a message 

        .. seealso:: :func:`MPI_Pool.mod_import()`
        """
        if self.comm is None:
            sys.setrecursionlimit(10000)
            self.max_binary_chunk = max_binary_chunk
            self.logger.setLevel(log_level)
            try:
                path = os.environ['VIRTUAL_ENV'] + '/bin/mpi_pool_v2.py'
            except KeyError:
                path = distutils.spawn.find_executable('mpi_pool_v2.py')
            cwd = os.getcwd()

            self.nprocs = nprocs
            if self.nprocs == None: # The command has been called through mpirun
                self.mpirun = True
                self.nprocs = get_avail_procs()
            self.logger.debug("start: spawn [before]")
            self.comm = MPI.COMM_SELF.Spawn(sys.executable,
                                            args=[path],
                                            maxprocs=self.nprocs)
            self.logger.debug("start: barrier")
            self.comm.Barrier()
            self.logger.debug("start: spawn [after]")
            
            # Broadcast cwd
            self.logger.debug("start: broadcast [before]")
            self.comm.bcast((cwd, max_binary_chunk, log_level), root=MPI.ROOT)
            self.logger.debug("start: broadcast [after]")
            
    def stop(self):
        r""" Stop the pool of processes
        """
        if self.comm is not None:
            self.logger.debug("stop: barrier")
            self.comm.Barrier()
            self.logger.debug("stop: broadcast [before]")
            # Stop children
            bcast_tuple = ("STOP",)
            self._binary_bcast(bcast_tuple)
            self.logger.debug("stop: broadcast [after]")
            # Gather any error
            self.logger.debug("stop: gather [before]")
            fval = self._binary_gather()
            self.logger.debug("stop: gather [after]")
            # Disconnect
            # Check whether somebody is still connected
            self.logger.debug("stop: free [before]")
            self.comm.Free()
            # self.comm.Disconnect()
            self.logger.debug("stop: free [after]")
            self.comm = None
            self.max_binary_chunk = None

    def split_data(self, x_list, kw_list, splitted=False):
        r""" Split the list of arguments in ``x_list`` into ``nprocs`` chunks and identify them by the keywords in ``kw_list``.

        Args:
          x_list (list): list of ``m`` arguments splittable in ``nprocs`` chunks
          kw_list (list): list of ``m`` strings used to identify the arguments
          splitted (bool): whether the input is already splitted

        Returns:
          (:class:`list<list>` [nprocs]) -- list of dictionaries containing the chucks
        """
        n = self.nprocs
        if len(x_list) != len(kw_list):
            raise ValueError("len(x_list)=%d , len(kw_list)=%d" % (len(x_list),
                                                                   len(kw_list)))
        split = [{} for i in range(n)]
        for x, kw in zip(x_list, kw_list):
            if splitted:
                for i,d in enumerate(split):
                    d[kw] = x[i]
            else:
                # Split the input data
                ns = [len(x) // n]*n
                for i in range(len(x) % n): ns[i] += 1
                for i in range(1,n): ns[i] += ns[i-1]
                ns.insert(0,0)
                # Update the output dictionary
                for i,d in enumerate(split):
                    d[kw] = x[ns[i]:ns[i+1]]
        return split

    def set_log_level(self, log_level):
        self.logger.debug("set_log_level: barrier")
        self.comm.Barrier()
        self.logger.setLevel(log_level)
        self.logger.debug("set_log_level: broadcast [before]")
        bcast_tuple = ("SET_LOG_LEVEL", log_level)
        self._binary_bcast(bcast_tuple)
        self.logger.debug("set_log_level: broadcast [after]")
        # Gather any error
        self.logger.debug("set_lot_level: gather [before]")
        fval = self._binary_gather()
        self.logger.debug("set_log_level: gather [after]")
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")
        
    def mod_import(self, import_set):
        r""" Make the children processes import a list of modules

        Given a set/list of tuples ``(m1, m2, m3)`` the children processes are asked to
        import the modules using the following commands.

        .. code-block:: python

           from m1 import m2 as m3

        if ``m1`` is not ``None``, otherwise

        .. code-block:: python

           import m2 as m3

        Args:
          import_set (set): set/list of tuples ``(m1, m2, m3)``
        
        """
        self.logger.debug("mod_import: barrier")
        self.comm.Barrier()
        self.logger.debug("mod_import: broadcast [before]")
        bcast_tuple = ("IMPORT", import_set)
        self._binary_bcast(bcast_tuple)
        self.logger.debug("mod_import: broadcast [after]")
        # Gather any error
        self.logger.debug("mod_import: gather [before]")
        fval = self._binary_gather()
        self.logger.debug("mod_import: gather [after]")
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")
            
    def map(self, f, obj_scatter=None, obj_bcast=None,
            dmem_key_in_list=None,
            dmem_arg_in_list=None,
            obj=None, reduce_obj=None, reduce_args=None):
        r""" Submit a job to the pool.

        Execute function ``f`` with scattered input ``obj_scatter`` and
        broadcasted input ``obj_bcast``.
        ``f`` should have the following format:

        ``obj_gather = f(**obj_scatter, **obj_bcast, **distr_mem[dmem_key_in_list])``

        where ``disrt_mem`` is a data structure containing data that is
        stored on the nodes, ``scatter_obj`` is a dictionary with the input data that is
        scattered to the nodes, ``obj_bcast`` is a dictionary with the input data
        that is broadcasted to the nodes, ``obj_gather`` is the data structure that is
        gathered from the nodes.

        If ``obj`` is not ``None``, ``f`` must be a string identifying the method
        ``obj.f``. If ``obj`` is a string, then it identifies an object stored
        in memory.

        Args:
          f (:class:`object` or :class:`str`): function or string identifying the
            function in object ``obj``
          obj_scatter (:class:`list` of :class:`dict`): input already splitted by
            :meth:`MPI_pool.split_data`
          obj_bcast (dict): dictionary with keys the input names of ``f`` and
            values the values taken by the keys.
          dmem_key_in_list (list): list of string containing the keys
            to be fetched (or created with default ``None`` if missing) from the
            distributed memory and provided as input to ``f``.
          dmem_arg_in_list (list): list of string containing the argument keywords
            to map fetched elements from the distributed memory to actual
            arguments of ``f``. Must be the same length of ``dmem_key_in_list``.
          obj (object): object where to find function ``f``.
          reduce_obj (object): object :class:`ReduceObject` defining the reduce
            method to be applied (if any)   
          reduce_args (object): arguments to be provided to ``reduce_object``,
            already splitted using :meth:`MPI_pool.split_data`.

        Returns:
          (:class:`list` [``nprocs``]) -- (ordered) outputs from all the processes
        """
        self.logger.debug("map: barrier")
        self.comm.Barrier()
        
        # Prepare scatter object
        if obj_scatter is not None:
            if len(obj_scatter) != self.nprocs:
                raise ValueError("The splitted input is not consistent with " + \
                                 "the number of processes")
        else:
            obj_scatter = [{} for i in range(self.nprocs)]

        # Prepare broadcast object
        if obj_bcast is None:
            obj_bcast = {}

        # Prepare dmem_key_in_list object
        if dmem_key_in_list is None:
            dmem_key_in_list = []

        # Prepare dmem_arg_in_list object
        if dmem_arg_in_list is None:
            dmem_arg_in_list = []

        if len(dmem_arg_in_list) != len(dmem_key_in_list):
            raise ValueError("The len(dmem_arg_in_list) != len(dmem_key_in_list) " + \
                             "(%d != %d)" % (len(dmem_arg_in_list), len(dmem_key_in_list)))

        # Prepare reduce object
        if reduce_args is not None:
            if len(reduce_args) != self.nprocs:
                raise ValueError("The splitted reduce_args is not consistent with "+\
                                 "the number of processes")
            split_red_args = reduce_args
        else:
            split_red_args = [{} for i in range(self.nprocs)]

        # Broadcast function and parameters
        bcast_tuple = ("MAP", obj, f, obj_bcast,
                       dmem_key_in_list, dmem_arg_in_list,
                       reduce_obj)
        self.logger.debug("map #1: broadcast")
        self._binary_bcast(bcast_tuple)

        # Scatter reduce arguments
        self.logger.debug("map #2: scatter")
        self._binary_scatter(split_red_args)

        # Scatter the data
        self.logger.debug("map #3: scatter")
        self._binary_scatter(obj_scatter)

        # Gather the results
        self.logger.debug("map #4: gather")
        fval = self._binary_gather()
        
        # Check for exceptions
        for v in fval:
            fail = False
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")

        if reduce_obj is not None:
            fval = reduce_obj.outer_reduce(fval, reduce_args)
            
        return fval

    def map_alloc_dmem(self, f, obj_scatter=None, obj_bcast=None,
                       dmem_key_in_list=None,
                       dmem_arg_in_list=None,
                       dmem_key_out_list=None,
                       obj=None, reduce_obj=None, reduce_args=None):
        r""" Submit a job to the pool.

        Execute function ``f`` with scattered input ``obj_scatter`` and
        broadcasted input ``obj_bcast``.
        ``f`` should have the following format:

        ``(**distr_mem[dmem_key_out_list]) = f(**obj_scatter, **obj_bcast, **distr_mem[dmem_key_in_list])``

        where ``disrt_mem`` is a data structure containing data that is
        stored on the nodes, ``scatter_obj`` is a dictionary with the input data that is
        scattered to the nodes, ``obj_bcast`` is a dictionary with the input data
        that is broadcasted to the nodes, ``obj_gather`` is the data structure that is
        gathered from the nodes.

        If ``obj`` is not ``None``, ``f`` must be a string identifying the method
        ``obj.f``.

        Args:
          f (:class:`object` or :class:`str`): function or string identifying the
            function in object ``obj``
          obj_scatter (:class:`list` of :class:`dict`): input already splitted by
            :meth:`MPI_pool.split_data`
          obj_bcast (dict): dictionary with keys the input names of ``f`` and
            values the values taken by the keys.
          dmem_key_in_list (list): list of string containing the keys
            to be fetched (or created with default ``None`` if missing) from the
            distributed memory and provided as input to ``f``.
          dmem_arg_in_list (list): list of string containing the argument keywords
            to map fetched elements from the distributed memory to actual
            arguments of ``f``. Must be the same length of ``dmem_key_in_list``.
          dmem_key_out_list (list): list of keys to be assigned to the outputs
            beside the first one
          obj (object): object where to find function ``f``.
          reduce_obj (object): object :class:`ReduceObject` defining the reduce
            method to be applied (if any)   
          reduce_args (object): arguments to be provided to ``reduce_object``,
            already splitted using :meth:`MPI_pool.split_data`.

        """
        self.logger.debug("map_alloc_dmem: barrier")
        self.comm.Barrier()
        
        # Prepare scatter object
        if obj_scatter is not None:
            if len(obj_scatter) != self.nprocs:
                raise ValueError("The splitted input is not consistent with " + \
                                 "the number of processes")
        else:
            obj_scatter = [{} for i in range(self.nprocs)]

        # Prepare broadcast object
        if obj_bcast is None:
            obj_bcast = {}

        # Prepare dmem_key_in_list object
        if dmem_key_in_list is None:
            dmem_key_in_list = []

        # Prepare dmem_arg_in_list object
        if dmem_arg_in_list is None:
            dmem_arg_in_list = []

        if len(dmem_arg_in_list) != len(dmem_key_in_list):
            raise ValueError("The len(dmem_arg_in_list) != len(dmem_key_in_list) " + \
                             "(%d != %d)" % (len(dmem_arg_in_list), len(dmem_key_in_list)))

        # Prepare dmem_key_out_list object
        if dmem_key_out_list is None:
            dmem_key_out_list = []

        # Prepare reduce object
        if reduce_args is not None:
            if len(reduce_args) != self.nprocs:
                raise ValueError("The splitted reduce_args is not consistent with "+\
                                 "the number of processes")
            split_red_args = reduce_args
        else:
            split_red_args = [{} for i in range(self.nprocs)]

        # Broadcast function and parameters
        bcast_tuple = (
            "MAP_ALLOC_DMEM",
            obj, f, obj_bcast, dmem_key_in_list, dmem_arg_in_list,
            dmem_key_out_list, reduce_obj)
        self.logger.debug("map_alloc_dmem #1: broadcast")
        self._binary_bcast(bcast_tuple)

        # Scatter reduce arguments
        self.logger.debug("map_alloc_dmem #2: scatter")
        self._binary_scatter(split_red_args)

        # Scatter the data
        self.logger.debug("map_alloc_dmem #3: scatter")
        self._binary_scatter(obj_scatter)

        # Gather the results
        self.logger.debug("map_alloc_dmem #4: gather")
        fval = self._binary_gather()
        
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")

    def alloc_dmem(self, **kwargs):
        r""" Allocate data on distributed memory. ``kwargs`` defines the names used in the distributed memory dictionary.
        """
        self.logger.debug("alloc_dmem: barrier")
        self.comm.Barrier()
        self.logger.debug("alloc_dmem: bcast [before]")
        bcast_tuple = ("ALLOC_DMEM", kwargs)
        self._binary_bcast(bcast_tuple)
        self.logger.debug("alloc_dmem: bcast [after]")
        # Gather any error
        self.logger.debug("alloc_dmem: gather [before]")
        fval = self._binary_gather()
        # fval = self.comm.gather(None, root=MPI.ROOT)
        self.logger.debug("alloc_dmem: gather [after]")
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")

    def get_dmem(self, *args):
        r""" Retrieve data from the distributed memory.

        Args:
          args (str): list of string containing the keys
            to be fetched (or created with default ``None`` if missing) from the
            distributed memory and provided as input to ``f``.

        Returns:
          (:class:`list` [``nprocs``]) -- list of tuples containing the data retrievered.
        """
        self.logger.debug("get_dmem: barrier")
        self.comm.Barrier()
        self.logger.debug("get_dmem: bcast [before]")
        bcast_tuple = ("GET_DMEM", args)
        self._binary_bcast(bcast_tuple)
        self.logger.debug("get_dmem: bcast [after]")
        # Gather any error
        self.logger.debug("get_dmem: gather [before]")
        fval = self._binary_gather()
        self.logger.debug("get_dmem: gather [after]")
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")
        return fval

    def pop_dmem(self, *args):
        r""" Retrieve and remove data from the distributed memory.

        Args:
          args (str): list of string containing the keys
            to be fetched (or created with default ``None`` if missing) from the
            distributed memory and provided as input to ``f``.

        Returns:
          (:class:`list` [``nprocs``]) -- list of tuples containing the data retrievered.
        """
        self.logger.debug("pop_dmem: barrier")
        self.comm.Barrier()
        self.logger.debug("pop_dmem: bcast [before]")
        bcast_tuple = ("POP_DMEM", args)
        self._binary_bcast(bcast_tuple)
        self.logger.debug("pop_dmem: bcast [after]")
        # Gather any error
        self.logger.debug("pop_dmem: gather [before]")
        fval = self._binary_gather()
        # fval = self.comm.gather(None, root=MPI.ROOT)
        self.logger.debug("pop_dmem: gather [after]")
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")
        return fval

    def list_dmem(self):
        r""" List keys in the distributed dictionaries

        Returns:
          (:class:`list` [``nprocs``]) -- list of strings
        """
        self.logger.debug("list_dmem: barrier")
        self.comm.Barrier()
        self.logger.debug("list_dmem: bcast [before]")
        bcast_tuple = ("LIST_DMEM",)
        self._binary_bcast(bcast_tuple)
        self.logger.debug("list_dmem: bcast [after]")
        # Gather any error
        self.logger.debug("list_dmem: gather [before]")
        fval = self._binary_gather()
        self.logger.debug("list_dmem: gather [after]")
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")
        return fval

    def clear_dmem(self):
        r""" Clear the distributed dictionaries
        """
        self.logger.debug("clear_dmem: barrier")
        self.comm.Barrier()
        self.logger.debug("clear_dmem: bcast [before]")
        bcast_tuple = ("CLEAR_DMEM",)
        self._binary_bcast(bcast_tuple)
        self.logger.debug("clear_dmem: bcast [after]")
        # Gather any error
        self.logger.debug("clear_dmem: gather [before]")
        fval = self._binary_gather()
        self.logger.debug("clear_dmem: gather [after]")
        # Check for exceptions
        fail = False
        for v in fval:
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")
            
class ReduceObject(object):
    r""" [Abstract] Generic object to be passed to MPI methods in order to define reduce operations.
    """
    def __init__(self):
        raise NotImplementedError("[Abstract]: needs to be extended")
    def inner_reduce(self, x, *args, **kwargs):
        r""" [Abstract] Reduce function called interally by every process
        """
        raise NotImplementedError("[Abstract]: needs to be extended")
    def outer_reduce(self, x, *args, **kwargs):
        r""" [Abstract] Reduce function called by the root process
        """
        raise NotImplementedError("[Abstract]: needs to be extended")


##################
# LEGACY VERSION #
##################    
class MPI_Pool_v1(object):
    r""" [LEGACY] Returns (but not start) a pool of ``nprocs`` processes

    Usage example:

    .. code-block:: python
    
        import numpy as np
        import numpy.random as npr
        import mpi_map

        class Operator(object):
            def dot(self, x, A):
                return np.dot(A,x.T).T

        def set_A(A):
            return (None,A)

        nprocs = 2
        op = Operator()
        A = npr.randn(5*5).reshape(5,5)

        import_set = set([("numpy","np")])
        pool = mpi_map.MPI_Pool()
        pool.start(nprocs, import_set)
        try:
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
    """
    
    def __init__(self):
        self.mpirun = False
        self.nprocs = None
        self.comm = None
        
    def start(self, nprocs=None, import_set=set()):
        r""" Start the pool of processes

        Args:
          nprocs (int): number of processes. If ``None`` then ``MPI.COMM_WORLD.Get_size()``
            processes will be started
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field``

        """
        if self.comm is None:
            sys.setrecursionlimit(10000)
            try:
                path = os.environ['VIRTUAL_ENV'] + '/bin/mpi_pool_v1.py'
            except KeyError:
                path = distutils.spawn.find_executable('mpi_pool_v1.py')
            cwd = os.getcwd()

            self.nprocs = nprocs
            if self.nprocs == None: # The command has been called through mpirun
                self.mpirun = True
                self.nprocs = get_avail_procs()
            logger.debug("MPI_Pool.start: spawn [before]")
            self.comm = MPI.COMM_SELF.Spawn(sys.executable,
                                            args=[path],
                                            maxprocs=self.nprocs)
            logger.debug("MPI_Pool.start: spawn [after]")
            
            # Broadcast cwd
            logger.debug("MPI_Pool.start: broadcast [before]")
            self.comm.bcast((cwd, import_set), root=MPI.ROOT)
            logger.debug("MPI_Pool.start: broadcast [after]")
            
    def stop(self):
        r""" Stop the pool of processes
        """
        if self.comm is not None:
            logger.debug("MPI_Pool.stop: broadcast [before]")
            # Stop children
            bcast_tuple = ("STOP", None, None, None, None, None, None, None)
            bcast_tuple_dill = dill.dumps(bcast_tuple)
            self.comm.bcast(bcast_tuple_dill, root=MPI.ROOT)
            logger.debug("MPI_Pool.stop: broadcast [after]")
            # Gather any error
            logger.debug("MPI_Pool.stop: gather [before]")
            fval = self.comm.gather(None, root=MPI.ROOT)
            logger.debug("MPI_Pool.stop: gather [after]")
            # Disconnect
            # Check whether somebody is still connected
            logger.debug("MPI_Pool.stop: free [before]")
            self.comm.Free()
            # self.comm.Disconnect()
            logger.debug("MPI_Pool.stop: free [after]")
            self.comm = None

    def split_data(self, x_list, kw_list, splitted=False):
        r""" Split the list of arguments in ``x_list`` into ``nprocs`` chunks and identify them by the keywords in ``kw_list``.

        Args:
          x_list (list): list of ``m`` arguments splittable in ``nprocs`` chunks
          kw_list (list): list of ``m`` strings used to identify the arguments
          splitted (bool): whether the input is already splitted

        Returns:
          (:class:`list<list>` [nprocs]) -- list of dictionaries containing the chucks
        """
        n = self.nprocs
        if len(x_list) != len(kw_list):
            raise ValueError("len(x_list)=%d , len(kw_list)=%d" % (len(x_list),
                                                                   len(kw_list)))
        split = [{} for i in range(n)]
        for x, kw in zip(x_list, kw_list):
            if splitted:
                for i,d in enumerate(split):
                    d[kw] = x[i]
            else:
                # Split the input data
                ns = [len(x) // n]*n
                for i in range(len(x) % n): ns[i] += 1
                for i in range(1,n): ns[i] += ns[i-1]
                ns.insert(0,0)
                # Update the output dictionary
                for i,d in enumerate(split):
                    d[kw] = x[ns[i]:ns[i+1]]
        return split

            
    def eval(self, f, obj_scatter=None, obj_bcast=None,
             dmem_key_in_list=None,
             dmem_arg_in_list=None,
             dmem_key_out_list=None,
             obj=None, reduce_obj=None, reduce_args=None,
             import_set=None):
        r""" Submit a job to the pool.

        Execute function ``f`` with scattered input ``obj_scatter`` and
        broadcasted input ``obj_bcast``.
        ``f`` should have the following format:

        ``obj_gather = f(**obj_scatter, **obj_bcast, **distr_mem[dmem_key_in_list])``

        or

        ``(obj_gather, **distr_mem[dmem_key_out_list]) = f(**obj_scatter, **obj_bcast, **distr_mem[dmem_key_in_list])``

        where ``disrt_mem`` is a data structure containing data that is
        stored on the nodes, ``scatter_obj`` is a dictionary with the input data that is
        scattered to the nodes, ``obj_bcast`` is a dictionary with the input data
        that is broadcasted to the nodes, ``obj_gather`` is the data structure that is
        gathered from the nodes.

        If ``obj`` is not ``None``, ``f`` must be a string identifying the method
        ``obj.f``.

        Args:
          f (:class:`object` or :class:`str`): function or string identifying the
            function in object ``obj``
          obj_scatter (:class:`list` of :class:`dict`): input already splitted by
            :meth:`MPI_pool.split_data`
          obj_bcast (dict): dictionary with keys the input names of ``f`` and
            values the values taken by the keys.
          dmem_key_in_list (list): list of string containing the keys
            to be fetched (or created with default ``None`` if missing) from the
            distributed memory and provided as input to ``f``.
          dmem_arg_in_list (list): list of string containing the argument keywords
            to map fetched elements from the distributed memory to actual
            arguments of ``f``. Must be the same length of ``dmem_key_in_list``.
          dmem_key_out_list (list): list of keys to be assigned to the outputs
            beside the first one
          obj (object): object where to find function ``f``.
          reduce_obj (object): object :class:`ReduceObject` defining the reduce
            method to be applied (if any)   
          reduce_args (object): arguments to be provided to ``reduce_object``,
            already splitted using :meth:`MPI_pool.split_data`.
          import_set (set): list of couples ``(module_name,as_field)`` to be imported
            as ``import module_name as as_field``

        Returns:
          (:class:`list` [``nprocs``]) -- (ordered) outputs from all the processes
        """
        if isinstance(f, str):
            f_in = f
        else:
            f_in = dill.dumps(f)
        obj_dill = dill.dumps(obj)
        red_obj_dill = dill.dumps(reduce_obj)

        # Prepare import
        if import_set is None:
            import_set = set()

        # Prepare scatter object
        if obj_scatter is not None:
            if len(obj_scatter) != self.nprocs:
                raise ValueError("The splitted input is not consistent with " + \
                                 "the number of processes")
        else:
            obj_scatter = [{} for i in range(self.nprocs)]

        # Prepare broadcast object
        if obj_bcast is None:
            obj_bcast = {}

        # Prepare dmem_key_in_list object
        if dmem_key_in_list is None:
            dmem_key_in_list = []

        # Prepare dmem_arg_in_list object
        if dmem_arg_in_list is None:
            dmem_arg_in_list = []

        if len(dmem_arg_in_list) != len(dmem_key_in_list):
            raise ValueError("The len(dmem_arg_in_list) != len(dmem_key_in_list) " + \
                             "(%d != %d)" % (len(dmem_arg_in_list), len(dmem_key_in_list)))

        # Prepare dmem_key_out_list object
        if dmem_key_out_list is None:
            dmem_key_out_list = []

        # Prepare reduce object
        if reduce_args is not None:
            if len(reduce_args) != self.nprocs:
                raise ValueError("The splitted reduce_args is not consistent with "+\
                                 "the number of processes")
            split_red_args = reduce_args
        else:
            split_red_args = [{} for i in range(self.nprocs)]

        # Broadcast function and parameters
        bcast_tuple = (obj_dill, f_in, obj_bcast, dmem_key_in_list, dmem_arg_in_list,
                       dmem_key_out_list, red_obj_dill, import_set)
        bcast_tuple_dill = dill.dumps(bcast_tuple)
        self.comm.bcast(bcast_tuple_dill, root=MPI.ROOT)
        logger.debug("MPI_Pool.eval: broadcast")


        # Scatter reduce arguments
        self.comm.scatter(split_red_args, root=MPI.ROOT)
        logger.debug("MPI_Pool.eval: scatter")

        # Scatter the data
        self.comm.scatter(obj_scatter, root=MPI.ROOT)
        logger.debug("MPI_Pool.eval: scatter")

        # Gather the results
        fval = self.comm.gather(None,root=MPI.ROOT)
        logger.debug("MPI_Pool.eval: gather")
        # Check for exceptions
        for v in fval:
            fail = False
            if isinstance(v, tuple) and isinstance(v[0], Exception):
                print (v[1])
                fail = True
        if fail:
            self.stop()
            raise RuntimeError("Some of the MPI processes failed")

        if reduce_obj is not None:
            fval = reduce_obj.outer_reduce(fval, reduce_args)
            
        return fval

class MPI_Pool(MPI_Pool_v1):
    pass
