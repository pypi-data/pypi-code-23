from __future__ import absolute_import, division

from numpy import asarray, empty_like, isfinite
from scipy.stats import norm, rankdata


def quantile_gaussianize(x):
    """Normalize a sequence of values via rank and Normal c.d.f.

    Args:
        x (array_like): sequence of values.

    Returns:
        Gaussian-normalized values.

    Example:

    .. doctest::

        >>> from scipy_sugar.stats import quantile_gaussianize
        >>> print(quantile_gaussianize([-1, 0, 2]))
        [-0.67448975  0.          0.67448975]
    """

    x = asarray(x, float).copy()
    ok = isfinite(x)
    x[ok] *= -1
    y = empty_like(x)
    y[ok] = rankdata(x[ok])
    y[ok] = norm.isf(y[ok] / (sum(ok) + 1))
    y[~ok] = x[~ok]
    return y
