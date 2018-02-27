
from __future__ import absolute_import

import xarray as xr
import numpy as np
import warnings


def _findpolymin(coeffs, bounds=(-np.inf, np.inf)):
    '''
    Minimize a polynomial given the coefficients on [x^1, x^2, ...]

    .. note::

        The coefficients given in the ``coeffs`` list must be in _ascending_
        power order and must not contain the zeroth-order term.


    Parameters
    ----------
    coeffs: :py:class `~xarray.DataArray`
        coefficients on a len(coeffs)-order polynomial in ascending power order
        _not_ including the zeroth-order term.

    bounds: list
       min and max temp values at which to find minimum

    Returns
    -------
        int: minimizing value of the polynomial (not the minimum value)

    '''
    minx = float(min(bounds))
    maxx = float(max(bounds))

    # Construct the derivative
    # derivcoeffs = np.array(coeffs) * np.arange(1, len(coeffs) + 1)
    # roots = np.roots(derivcoeffs[::-1])

    roots = np.poly1d(list(coeffs[::-1]) + [0]).deriv().roots

    # Filter out complex roots; note: have to apply real_if_close to individual
    # values, not array until filtered
    possibles = (
        list(filter(
            lambda root:
                np.real_if_close(root).imag == 0
                and np.real_if_close(root) >= minx
                and np.real_if_close(root) <= maxx,
            roots)))

    possibles = list(np.real_if_close(possibles)) + [minx, maxx]

    with warnings.catch_warnings():  # catch warning from using infs
        warnings.simplefilter("ignore")

        values = np.polyval(
            list(coeffs[::-1]) + [0],
            np.real_if_close(possibles))

    # polyval doesn't handle infs well
    if minx == -np.inf:
        if len(coeffs) % 2 == 0:  # largest power is even
            values[-2] = -np.inf if coeffs[-1] < 0 else np.inf
        else:  # largest power is odd
            values[-2] = np.inf if coeffs[-1] < 0 else -np.inf

    if maxx == np.inf:
        values[-1] = np.inf if coeffs[-1] > 0 else -np.inf

    index = np.argmin(values)

    return possibles[index]


def minimize_polynomial(da, dim='prednames', bounds=(-np.inf, np.inf)):
    '''
    Finds the minimizing values of polynomials given an array of coefficients

    .. note::

        The coefficients along the dimension ``dim`` must be in _ascending_
        power order and must not contain the zeroth-order term.


    Parameters
    ----------
    da: DataArray
        :py:class:`~xarray.DataArray` of coefficients of a
        ``(da.size[dim])``-order polynomial in ascending power order along the
        dimension ``dim``. The coefficients must not contain the zeroth-order
        term.

    dim: str, optional
        dimension along which to evaluate the coefficients (default
        ``prednames``)

    bounds: list, optional
        domain on the polynomial within which to search for the minimum value,
        default ``(-inf, inf)``

    Returns
    -------
    DataArray
        :py:class:`~xarray.DataArray` in the same shape as da, with the
        minimizing value of the polynomial raised to the appropriate power
        in place of each coefficient

    Examples
    --------

    Create an array with two functions:

    ..math::

        \begin{array}{rcl}
            f_1 & = & x^2 \\
            f_2 & = & -x^2 + 2x
        \end{array}

    This is specified as a 2-dimensional :py:class:`xarray.DataArray`:

    .. code-block:: python

        >>> da = xr.DataArray(
        ...     [[0, 1],   # x^2
        ...      [2, -1]], # -x^2 + 2x
        ...     dims=('spec', 'x'),
        ...     coords={'spec': ['f1', 'f2'], 'x': ['x1', 'x2']})
        ...

    These functions can be minimized using
    :py:func:`impax.mins.minimize_polynomial`:

    .. code-block:: python

        >>> minimize_polynomial(
        ...     da, dim='x') # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        ...
        <xarray.DataArray (spec: 2, x: 2)>
        array([[  0.,   0.],
               [-inf,  inf]])
        Coordinates:
          * x        (x) ... 'x1' 'x2'
          * spec     (spec) ... 'f1' 'f2'

    Use the same function, but impose the domain limit :math:`[2, 4]`:

    .. code-block:: python

        >>> minimize_polynomial(
        ...     da, dim='x', bounds=[2, 4])
        ...     # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        <xarray.DataArray (spec: 2, x: 2)>
        array([[  2.,   4.],
               [  4.,  16.]])
        Coordinates:
          * x        (x) ... 'x1' 'x2'
          * spec     (spec) ... 'f1' 'f2'

    '''
    t_star_values = np.apply_along_axis(
        _findpolymin, da.get_axis_num(dim), da.values, bounds=bounds)

    if t_star_values.shape != tuple(
            [s for i, s in enumerate(da.shape) if i != da.get_axis_num(dim)]):

        raise ValueError(
            '_findpolymin returned an unexpected shape: {}'
            .format(t_star_values.shape))

    t_star = xr.DataArray(
        t_star_values,
        dims=tuple([d for d in da.dims if d != dim]),
        coords={c: da.coords[c] for c in da.coords.keys() if c != dim})

    t_star = t_star.expand_dims(dim, axis=da.get_axis_num(dim))

    # RPolynomial of length 4 should return terms t, t^2, t^3, t^4.
    t_star_poly = xr.concat(
        [t_star**i for i in range(1, len(da.coords[dim])+1)],
        dim=da.coords[dim])

    return t_star_poly
