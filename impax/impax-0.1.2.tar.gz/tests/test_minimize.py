
from __future__ import absolute_import
import impax.mins
import xarray as xr
import numpy as np

import pytest


def find_polymin_from_roots(roots, bounds=(-np.inf, np.inf), scale=1):
    r'''
    Find mimimum value of integral of polynomial defined by roots

    Helper function used in test fixtures to take integral of polynomial
    created from a list of roots and to find the minimizing value

    Parameters
    ----------
    roots : list
        List of roots of the polynomial to be integrated
    bounds : tuple
        Bounds to place on the minizing step
    scale : int
        Scalar to multiply by the polynomial created from roots

    Examples
    --------
    The simplest polynomial that can be examined here has no roots, e.g.:

    .. math::

        [] \rightarrow f(x)=1 \rightarrow \integral_x f(x) = 1x

    This function has no roots, and thus its integral has no minimum:

    .. code-block:: python

        >>> minimizer, minimum_value = find_polymin_from_roots([])
        >>> minimizer
        -inf
        >>> minimum_value
        -inf

    A more complex polynomial may have multiple roots:

    .. math::

        [0, 2]\rightarrow f(x)=(x-0)(x-2)\rightarrow\integral_x f(x)=1/3x^3-x^2

    This function has roots 0, 2, but still has an infinite minimum value.
    Bounds can be placed on the minimization problem with the `bounds`
    argument:

    ..code-block:: python

        >>> minimizer, minimum_value = find_polymin_from_roots(
        ...     [0, 2],
        ...     bounds=(0, np.inf))
        ...
        >>> minimizer
        2.0
        >>> minimum_value == 8.0/3.0 - 4
        True
    '''

    roots = np.array(roots)

    p = np.poly1d(roots, r=True) * scale

    p2 = np.poly1d(list(p.coeffs / np.arange(len(p.coeffs), 0, -1)) + [0])

    candidates = np.array(
        list(roots[(roots >= bounds[0]) & (roots <= bounds[1])])
        + list(bounds))

    vals = np.array([
        p2(c)
        if not np.isinf(c)
        else (
            np.sign(p2.coeffs[0]) * np.sign(c) * np.inf
            if (len(p2.coeffs) % 2 == 0)
            else np.sign(p2.coeffs[0]) * np.inf)
        for c in candidates])

    return candidates[vals.argmin()], min(vals)


def test_roots_generator():
    '''
    Test function to minimize integral of polynomial created from list of roots
    '''

    assert find_polymin_from_roots([0])[0] == 0
    assert find_polymin_from_roots([1])[0] == 1
    assert find_polymin_from_roots([-1])[0] == -1
    assert find_polymin_from_roots([0], scale=-1)[0] == -np.inf
    assert find_polymin_from_roots([0], bounds=(-10, 5), scale=-1)[0] == -10
    assert find_polymin_from_roots([], bounds=(0, np.inf))[0] == 0
    assert find_polymin_from_roots([], bounds=(1, np.inf))[0] == 1


@pytest.fixture(params=range(4))
def known_minimized_polynomial(request):

    if request.param == 0:
        test_roots = np.array([3, 5, -1, -23])
        bounds = (-np.inf, np.inf)
        scale = 1
        known_minimizer = -np.inf

    elif request.param == 1:
        test_roots = np.array([3, 5, -1, -23])
        bounds = (0, np.inf)
        scale = 1
        known_minimizer = 0

    elif request.param == 2:
        test_roots = np.array([3, 5, -1, -23])
        bounds = (-23, 50)
        scale = 1
        known_minimizer = -1

    elif request.param == 3:
        test_roots = np.array([3, 5, -1, -23])
        bounds = (-23, 5)
        scale = -1
        known_minimizer = -23

    minimizer, minimized = find_polymin_from_roots(
        test_roots, bounds=bounds, scale=scale)

    assert known_minimizer == minimizer

    p = np.poly1d(test_roots, r=True) * scale
    p2 = np.poly1d(list(p.coeffs / np.arange(len(p.coeffs), 0, -1)) + [0])

    da = xr.DataArray(
        p2.coeffs[slice(-2, None, -1)],
        dims=('predname', ),
        coords={'predname': ['x', 'x2', 'x3', 'x4', 'x5']})

    yield da, 'predname', bounds, minimizer


def test_polymin_for_function_constructed_from_roots(
        known_minimized_polynomial):

    da, dim, bounds, polymin = known_minimized_polynomial

    minned = float(
        impax.mins.minimize_polynomial(da, 'predname', bounds)
        .sel(predname='x'))

    assert (polymin == minned)


def test_polymin_for_arbitrary_polynomial_within_ranges():
    test_da = xr.DataArray(
        (np.random.random((6, 10, 10)) - 0.5) * 12,
        dims=('coeffs', 'var1', 'var2'),
        coords={'coeffs': range(1, 7)})

    minx = impax.mins.minimize_polynomial(test_da, 'coeffs', bounds=[-10, 20])

    control_field = xr.DataArray(
        np.vstack([np.arange(-15, 25, 0.1)**i for i in range(1, 7)]),
        dims=('coeffs', 'x'),
        coords={'x': np.arange(-15, 25, 0.1), 'coeffs': range(1, 7)})

    controlled = (
        (test_da * control_field).sum(dim='coeffs')
        - (test_da * minx).sum(dim='coeffs'))

    limrange = controlled.where((controlled.x >= -10) & (controlled.x <= 20))

    assert limrange.fillna(0).min() >= 0
    assert (limrange.min(dim='x') >= 0).all()


def test_polymin_for_polynomials_with_known_minima():
    '''
    Tests impax.mins._findpolymin for functions with known minima
    '''

    # x^2 --> 0
    assert impax.mins._findpolymin([0, 1], (-np.inf, np.inf)) == 0

    # x^2 - 2x --> 1
    assert impax.mins._findpolymin([-2, 1], (-np.inf, np.inf)) == 1

    # x^3 --> -np.inf
    assert impax.mins._findpolymin([0, 0, 1], (-np.inf, np.inf)) == -np.inf


def test_polymin_for_polynomials_with_known_minima_and_bounds():

    # -x^2, [0, 5] --> 5
    assert impax.mins._findpolymin([0, -1], (0, 5)) == 5

    # x^2, [3, 9] --> 3
    assert impax.mins._findpolymin([0, 1], (3, 9)) == 3


def test_ambiguous_cases():

    # -x^2, [-1, 1] --> -1?
    assert impax.mins._findpolymin([0, -1], (-1, 1)) == -1

    # 0, [-1, 1] --> -1?
    assert impax.mins._findpolymin([0, 0], (-1, 1)) == -1
