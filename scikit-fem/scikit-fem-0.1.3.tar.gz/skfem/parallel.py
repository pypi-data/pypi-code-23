# -*- coding: utf-8 -*-
"""

Utilities for parallel computing using petsc4py.

Additional dependencies:

conda install -c mpi4py mpi4py
conda install -c conda-forge petsc4py
pip install pymetis

"""
import numpy as np
from petsc4py import PETSc
from mpi4py import MPI
from skfem.assembly import Dofnum

def partition(m, N):
    """Use METIS for partitioning the mesh."""
    from pymetis import part_graph

    # find neighboring elements
    neighbors1 = m.f2t[0, m.t2f]
    neighbors2 = m.f2t[1, m.t2f]
    neighbors = np.vstack((neighbors1, neighbors2))

    # build adjacency information into a dict
    adj = dict(zip(np.arange(m.t.shape[1]), neighbors.T))
    for itr in range(len(adj)):
        adj[itr] = [x for x in adj[itr] if x != itr and x != -1]

    # call METIS
    _, part = part_graph(N, adj)

    # The resulting array is of length Nelems, consists
    # of integers and each separate integer refers to
    # separate subdomain.
    return np.array(part)

def par_assemble(asm_matrix, asm_vector, mesh, element):
    """Assemble system in parallel."""
    comm = PETSc.COMM_WORLD

    A = PETSc.Mat()
    A.create(comm)
    A.setType('aij')

    dofnum = Dofnum(mesh, element)

    A.setSizes((dofnum.N, dofnum.N))

    A.setUp()