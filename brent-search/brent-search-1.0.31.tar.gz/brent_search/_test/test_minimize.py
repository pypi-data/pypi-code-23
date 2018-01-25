from __future__ import division

from brent_search import minimize
from numpy.testing import assert_almost_equal, assert_array_less


def test_minimize_strictly_convex_up():
    def func(x, s):
        return (x - s)**2 - 0.8

    (x, fx, nfev) = minimize(lambda x: func(x, 0), -10, -5)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 9)

    (x, fx, nfev) = minimize(lambda x: func(x, 0), -10, 0)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 8)

    (x, fx, nfev) = minimize(lambda x: func(x, 0), -10, -9)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 11)

    (x, fx, nfev) = minimize(lambda x: func(x, 0), -10, 10)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 8)


def test_minimize_strictly_convex_down():
    def func(x, s):
        return (x - s)**2 - 0.8

    (x, fx, nfev) = minimize(lambda x: func(x, 0), -5, -10)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 9)

    (x, fx, nfev) = minimize(lambda x: func(x, 0), 0, -10)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 8)

    (x, fx, nfev) = minimize(lambda x: func(x, 0), -9, -10)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 11)

    (x, fx, nfev) = minimize(lambda x: func(x, 0), 10, -10)
    assert_almost_equal(x, 0)
    assert_almost_equal(fx, -0.8)
    assert_array_less(nfev, 8)


def test_minimize_strictly_convex_equal():
    def func(x, s):
        return (x - s)**2 - 0.8

    (x, fx, nfev) = minimize(lambda x: func(x, 0), -10, -10)
    assert_almost_equal(x, -10)
    assert_almost_equal(fx, func(-10, 0))
    assert_array_less(nfev, 3)

    (x, fx, nfev) = minimize(lambda x: func(x, 0), +10, +10)
    assert_almost_equal(x, +10)
    assert_almost_equal(fx, func(+10, 0))
    assert_array_less(nfev, 3)


def test_minimize_asymptotic():
    def func(x):
        return -3 + 1 / x

    (x, _, niters) = minimize(func, a=1e-6, b=+10, rtol=1e-9)
    assert_almost_equal(x, 10)
    assert_array_less(niters, 69)

    (x, _, niters) = minimize(func, a=-10, b=-1e-6)
    assert_almost_equal(x, -1e-06)
    assert_array_less(niters, 6)
