#!/usr/bin/env python3

"""
Methods for simulating TDSE
"""

from ._krylov.exponential import expm_multiply
import numpy as np


def evolve_timestep(psi, Hmid, delta_t, expm_tolerance, krylov_maxdim):
    """
    Evolves the wavefunction ψ(x, t) to ψ(x, t+Δt) = U(t+Δt, t)ψ(x, t) using the exponential mid-point
    rule for the time-evolution operator, i.e.,

      U(t + Δt, t) ψ(x, t) = exp[-i Δt H(t + Δt/2) ] ψ(x, t),

    where H(t) is the time-dependent Hamiltonian matrix. The matrix exponential is calculated using
    Krylov-subspace projection of the matrix exponential.

    Parameters
    ----------

    psi : np.ndarray of complex numbers, shape (N)
        The wavefunction at time t, ψ(x, t).
    Hmid : object convertible to scipy.sparse.LinearOperator, shape (N,N)
        The time-dependent Hamiltonian matrix at time t + Δt/2
    delta_t : float
        Time-step
    expm_tolerance : float
        Relative tolerance for the matrix exponential operation (error of the
        norm of the resulting vector)
    krylov_maxdim : int, positive
        Maximum dimension of the Krylov subspace. Will raise Warnings if the 
        matrix exponential doesn't converge within the given subspace dimension.

    Returns
    -------

    psi_next : np.ndarray of complex numbers, shape (N)
        The wavefunction at time t + Δt
    """
    return expm_multiply(Hmid, psi, -1j * delta_t, expm_tolerance,
                         krylov_maxdim)


def complex_absorbing_potential(x, cap_width, cap_height):
    """Complex absorbing potential cos[pi/(2w)(x-x_boundary)]**2 for
    |x-x_boundary| < w"""
    def cap_fun(x):
        return -1.0j * cap_height * np.cos(np.pi / (2 * cap_width) * x)**2
    return np.piecewise(x + 0j,  # to make piecewise work with complex valued funs
                        [
                            np.fabs(x - x[0]) <= cap_width,
                            np.fabs(x - x[-1]) <= cap_width
                        ],
                        [
                            lambda x: cap_fun(x - x[0]),
                            lambda x: cap_fun(x - x[-1]),
                        ])
