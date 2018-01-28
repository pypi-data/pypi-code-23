"""
This module contains some optimization test functions.
"""

from .optimization import Optimization


# Himmelblau function
# Optimizing function: f(x) = (x^2 + y - 11)^2 + (x + y^2 -7)^2
# Finding: min
# Boundaries:
# x: -5 -> 5
# y: -5 -> 5

HIMMELBLAU = {
    'optimization': Optimization(
        optimizing_function=lambda x:
        (x[0]**2 + x[1] - 11)**2 + (x[0] + x[1]**2 - 7)**2,
        boundaries=[(-5.0, 5.0), (-5.0, 5.0)],
        no_dimensions=2,
        find_max=False
    ),
    'results': [
        (0.0, (3.0, 2.0)),
        (0.0, (-2.805118, 3.131312)),
        (0.0, (-3.779310, -3.283186)),
        (0.0, (3.584428, -1.848126))
    ]
}


# Rosenbrock function
# Optimizing function: f(x) = (1 - x)^2 + 100(y - x^2)^2
# Finding: min
# Boundaries:
# - x: -3 -> 3
# - y: -3 -> 3

ROSENBROCK = {
    'optimization': Optimization(
        optimizing_function=lambda x:
        (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2,
        boundaries=[(-3.0, 3.0), (-3.0, 3.0)],
        no_dimensions=2,
        find_max=False
    ),
    'results': [
        (1.36e-10, (1.0, 1.0))
    ]
}
