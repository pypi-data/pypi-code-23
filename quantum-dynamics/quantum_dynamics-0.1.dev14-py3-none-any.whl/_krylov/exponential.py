#!/usr/bin/env python3

"""
Implementation of matrix exponential using Krylov subspace methods.
"""

import warnings
import numpy as np
import scipy.linalg as la
import scipy.sparse.linalg as sla
import scipy.sparse as sp
from ._krylov_subspace import *


def expm_multiply(A, v, t=1, rtol=1e-5, max_krylov_dim=None,
                  return_krylov_dim=False):
    """
    Implementation of Krylov subspace based approximation for the matrix
    exponential exp(t*A)v. Reference implementation, not optimized.

    Parameters
    ----------
    A : linear operator, shape (N,N)
        This is the linear operator whose exponential we apply to the vector
        `v`. The only requirements are that (1) it's convertible to
        scipy.sparse.LinearOperator and (2) it's a map between vector spaces
        of same dimension.
    v : vector-like object, shape (N)
        This is the vector to which we apply the exponential of `A`. Should
        be compatible with `A`.
    t : real or complex number, [default = 1, optional]
        The scalar in the matrix exponential exp(t*A)v.
    rtol : real number, [default = 1e-5, optional]
        Requested relative error for exp(tA)v.
    max_krylov_dim : int, optional
        Maximal size of the Krylov subspace that will be used.
    return_krylov_dim: bool, [default = False, optional]
        If True, also the used Krylov subspace dimension is returned.

    Returns
    -------
    w : vector-like object, shape (N), dtype is complex if A or v is of
                                       complex type, otherwise float
        w = exp(tA)v
    krylov_subspace_dimension : int, optional
        Size of the Krylov subspace used in the calculation.

    Raises
    ------
    RuntimeWarning
        If could not achieve the requested relative error with the given
        maximum Krylov subspace size.
    """

    if not isinstance(A, (sla.LinearOperator, np.ndarray, np.matrix,
                          sp.spmatrix)):
        raise TypeError("A cannot be converted to a LinearOperator")

    if not A.shape[0] == A.shape[1]:
        raise TypeError("A's domain and codomain are of different sizes.")

    if not isinstance(v, (np.ndarray)):
        raise TypeError("v is not a numpy array")

    if len(v.shape) != 1 and v.shape[1] != 1:
        raise TypeError("v is not a 1D array.")

    if v.shape[0] != A.shape[0]:
        raise TypeError("Dimensions of A and v don't match.")

    input_v_is_a_column_vector = False
    if len(v.shape) != 1:
        v = v.reshape(v.shape[0])
        input_v_is_a_column_vector = True

    KS = KrylovSubspace(A, v, dim_estim=max_krylov_dim)

    maxiter = max_krylov_dim if max_krylov_dim else A.shape[0]

    for k in range(maxiter):

        KS.grow()

        Vm1, Hm1 = KS.get()

        exptHm1 = la.expm(t * Hm1)
        if KS.invariant:
            break
        else:
            rel_err = np.abs(exptHm1[-1, 0])
            if rel_err < rtol:
                break

    if max_krylov_dim and (k == max_krylov_dim - 1):
        warnings.warn(RuntimeWarning("""The matrix exponential did
not converge to desired accuracy with the given Krylov subspace size."""))

    # Compute the approximate result
    w = KS.β * Vm1 @ exptHm1[:, 0]

    if input_v_is_a_column_vector:
        w = np.reshape(w, (v.shape[0], 1))

    if return_krylov_dim:
        return w, KS.dim
    else:
        return w
