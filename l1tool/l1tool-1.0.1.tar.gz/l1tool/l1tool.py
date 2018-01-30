#!usr/env/bin python
#author: WU Dingcheng
import cvxpy as cvx
import numpy as np
from scipy.sparse import eye, csr_matrix, hstack, linalg


def gen_d2(n):
    """
    Generate the 2nd difference matrix.
    :param n: int, length of time series
    :return: csr_matrix, sparse matrix
    """
    I2 = eye(n - 2)
    O2 = csr_matrix((n - 2, 1))
    return hstack((I2, O2, O2)) + hstack((O2, -2 * I2, O2)) + hstack((O2, O2, I2))


def gen_d1(n):
    """
    Generate the 1st difference matrix
    :param n: int, length of time series
    :return: csr_matrix, sparse matrix
    """
    I1 = eye(n - 1)
    O1 = csr_matrix((n - 1, 1))
    return hstack((I1, O1)) - hstack((O1, I1))


def get_max_lam(y):
    """
    Calculate the max lambda value for given time series y
    :param y: np.array, time series given
    :return: float, max lambda value
    """
    D = gen_d2(len(y))
    ddt = D.dot(D.T)
    dy = D.dot(y)
    return np.linalg.norm(linalg.spsolve(ddt, dy), np.inf)


def get_max_rho(y):
    """
    Calculate the max rho value for given time series y,
    :param y: np.array, time series given
    :return: float, max rho value
    """
    D = gen_d1(len(y))
    ddt = D.dot(D.T)
    dy = D.dot(y)
    return np.linalg.norm(linalg.spsolve(ddt, dy), np.inf)


def l1filter(t,
             y,
             lam=1200,
             rho=80,
             periods=(365.25, 182.625),
             solver=cvx.MOSEK,
             verbose=False):
    """
    Do l1 regularize for given time series.
    :param t: np.array, time
    :param y: np.array, time series value
    :param lam: lambda value
    :param rho: rho value
    :param periods: list, periods, same unit as t
    :param solver: cvx.solver
    :param verbose: bool, show verbose or not
    :return: x, w, s, if periods is not None, else return x, w
    """
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    assert y.shape == t.shape

    n = len(t)
    D = gen_d2(n)

    x = cvx.Variable(n)
    w = cvx.Variable(n)
    errs = y - x - w
    seasonl = None
    if periods is not None:
        tpi_t = 2 * np.pi * t
        for period in periods:
            a = cvx.Variable()
            b = cvx.Variable()
            temp = a * np.sin(tpi_t / period) + b * np.cos(tpi_t / period)
            if seasonl is None:
                seasonl = temp
            else:
                seasonl += temp
        errs = errs - seasonl
    obj = cvx.Minimize(0.5 * cvx.sum_squares(errs) +
                       lam * cvx.norm(D * x, 1) +
                       rho * cvx.tv(w))
    prob = cvx.Problem(obj)
    prob.solve(solver=solver, verbose=verbose)
    if seasonl is not None:
        return np.array(x.value)[:, 0], np.array(w.value)[:, 0], np.array(seasonl.value)[:, 0]
    else:
        return np.array(x.value)[:, 0], np.array(w.value)[:, 0]
