#!/usr/bin/env python3

"""
Implementation of projecting linear operators to a Krylov subspace. A basis for
the Krylov subspace is searched with the standard Arnoldi iteration.
"""

import numpy as np
import scipy.sparse.linalg as sla


class KrylovSubspace(object):

    def __init__(self, A, v, dim_estim=None, invariance_tol=1e-8):
        """
        Initializes the Krylov Subspace class for a linear map A and vector v.

        Parameters
        ----------
        A : an object convertible to scipy.sparse.linalg.LinearOperator
            The linear map
        v : vector-like object which can be operated on by `A`
            The vector
        dim_estim : int, optional
            estimate for the required Krylov subspace dimension
        invariance_tol : float, optional
            If the residual vector norm is less than this, the Krylov subspace
            is considered to be invariant under `A`.

        """
        if A.shape[0] != A.shape[1]:
            raise TypeError("Given Matrix A is not a square matrix: %d × %d" %
                            (A.shape[0], v.shape[0]))

        if A.shape[0] != v.shape[0]:
            raise TypeError("Matrix and vector dimensions disagree: (%d × %d) vs %d" % (
                A.shape[0], A.shape[1], v.shape[0]))

        # Construct the matrix as a LinearOperator
        self.A = sla.aslinearoperator(A)
        self.v = v
        self.β = np.linalg.norm(self.v)
        self.invariance_tol = invariance_tol

        self.dim = 0
        dim_estim = dim_estim if dim_estim else np.min((self.A.shape[0] // 2,
                                                        50))

        self.dtype = np.dtype("complex") if np.iscomplexobj(
            A) or np.iscomplexobj(v) else np.dtype("float")

        # The projection matrix
        self.V = np.zeros((self.A.shape[0], dim_estim + 1), dtype=self.dtype)
        # Initialize the first step
        self.V[:, 0] = self.v / self.β

        # The projection of the linear map onto the subspace
        self.H = np.zeros((dim_estim + 1, dim_estim), dtype=self.dtype)

        # This will be set to true if the subspace is invariant under A
        self.invariant = False

    def _resize_storage(self):
        """Doubles the size of V and H if a larger basis does not fit in the
        allocated space."""
        if self.dim >= self.H.shape[1] - 1:

            new_max_dim = np.max((2 * self.dim, self.A.shape[0]))
            H_old = self.H
            self.H = np.zeros((new_max_dim + 1, new_max_dim),
                              dtype=H_old.dtype)
            self.H[:H_old.shape[0], :H_old.shape[1]] = H_old
            self.V = np.concatenate(
                (self.V, np.zeros((self.A.shape[0],
                                   new_max_dim + 1 - self.dim))),
                axis=1)

    def grow(self):
        """
        Calculates a single Arnoldi iteration using the modified Gram-Smidt
        orthonornoalization and increases the Krylov subspace dimension by one.

        Raises
        ------
        RuntimeError
            Returned if
                * the Krylov Subspace is already invariant
                * the Krylov Subspace size is maximal (then the subspace should
                  also be invariant)
        """

        self._resize_storage()

        if self.invariant:
            raise RuntimeError("Krylov Subspace already invariant.")

        elif self.dim == self.A.shape[0]:
            raise RuntimeError("Krylov Subspace is already maximal size.")

        self.dim += 1

        # Index of the last basis vector
        j = self.dim - 1
        p = self.A @ self.V[:, j]

        # MGS orthonormalization
        for i in range(self.dim):
            self.H[i, j] = np.vdot(self.V[:, i], p)
            p -= self.H[i, j] * self.V[:, i]

        self.H[j + 1, j] = np.linalg.norm(p)

        # Check if the Krylov subspace is invariant
        if np.abs(self.H[j + 1, j]) < self.invariance_tol:
            self.invariant = True
        else:
            self.V[:, j + 1] = p / self.H[j + 1, j]

    def get(self):
        """
        Returns
        -------
        V : np.ndarray, shape = ( dim(v), dim_krylov [+1] )
            The projector matrix from the original space to the Krylov subspace.
            The [+1] in the shape is used whenever we don't already have
            an invariant subspace
        H : np.ndarray, shape = ( dim_krylov[+1], dim_krylov+1 )
            The approximation of the original operator `A` in the Krylov
            subspace. The [+1] in the shape is used whenever we don't
            already have an invariant subspace.
        """
        if self.invariant:
            return self.V[:, :self.dim], self.H[:self.dim, :self.dim]
        else:
            return self.V[:, :self.dim +
                          1], self.H[:self.dim + 1, :self.dim + 1]
