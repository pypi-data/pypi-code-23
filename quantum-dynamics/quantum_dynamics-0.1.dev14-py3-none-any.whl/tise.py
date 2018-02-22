#!/usr/bin/env python3

"""
Extracted solution of ex4.4, solving eigenstates of 1D hydrogen.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.integrate import simps
from .utils import *


def get_initial_state(grid, potential, sparse_matrix_format='dia'):
    """
    Calculates the ground state ψ(x) of 1D quantum systems defined by the 
    time-independent Schrödinger equation

      H ψ(x) = E ψ(x),

    where the Hamiltonian is (in atomic units)

      H = [ -0.5 ∂^2/∂x^2 + V(x) ].

    The second derivative ∂^2/∂x^2 is approximated by a second order central finite-difference
    scheme.

    Parameters
    ----------

    grid : np.ndarray of floats, shape (N)
        The real space coordinate grid, should be uniform.
    potential : callable
        Function returning the model potential V(x). This function should take
        np.ndarray (`grid`) as the argument and return the potential values
        at these coordinates.
    sparse_matrix_format : str
        Format of the sparse matrices used in the calculation (BSR, COO, CSC,
        CSR or DIA)

    Returns
    -------

    psi : np.ndarray of floats or complex numbers, shape (N)
        The ground state wavefunction on the coordinate grid.
    H0 : scipy.sparse.dia_matrix of floats, shape (N,N)
        The time-independent Hamiltonian matrix as a sparse matrix with 
        DIAgonal storage scheme.
    """

    if not is_numpy_array_of_reals(grid):
        raise TypeError("Argument 'grid' was not a numpy array of real\
                        numbers")

    try:
        potential(np.array([1.0, 2.0, 3.0]))
    except:
        raise TypeError("Argument `potential` could not be called with a numpy\
                        array")

    if not isinstance(sparse_matrix_format, str):
        raise TypeError("Argument 'sparse_matrix_format' was not passed a\
                        string")

    sparse_matrix_format = sparse_matrix_format.lower()
    if not sparse_matrix_format in ["bsr", "coo", "csc", "csr", "dia"]:
        raise RuntimeError("Argument 'sparse_matrix_format' is not one of BSR,\
                           COO, CSC, CSR, or DIA")

    grid_size = grid.shape[0]
    dx = grid[1] - grid[0]
    dx2 = dx * dx

    H0 = sp.diags(
        [
            -0.5 / dx2 * np.ones(grid_size - 1),
            -0.5 / dx2 * np.ones(grid_size - 1),
            1.0 / dx2 * np.ones(grid_size) + potential(grid)
        ],
        [-1, 1, 0],
        format=sparse_matrix_format)

    # Diagonalize (note that our matrix is real symmetric so we use the
    # `eigsh`-routine instead of `eigs`).
    _, evecs = sla.eigsh(H0, k=1, which='SA')

    # Normalize the eigenvector
    psi0 = evecs[:, 0]
    norm = simps(np.abs(psi0)**2, x=grid)

    return psi0 / np.sqrt(norm), H0
