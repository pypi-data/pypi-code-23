"""Setup and initialization for tests."""

import os
import pytest
from py_opt_collection.optimization import Optimization, AlgorithmObject


project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture
def fix_source_code_dir():
    """Return the path of the current source code."""
    return project_dir + '/py_opt_collection'


@pytest.fixture
def fix_optimization_function():
    """Optimization function: x^4 + x^3 -3x^2 + 1, with x in [-3, 3]."""
    return lambda x: x[0] ** 4 + x[0] ** 3 - 3 * (x[0] ** 2) + 1


@pytest.fixture
def fix_optimization_object_kwargs():
    return {
        'optimizing_function': fix_optimization_function(),
        'boundaries': [(-3, 3)],
        'no_dimensions': 1,
        'find_max': False
    }


@pytest.fixture
def fix_optimization_object_kwargs_with_seed():
    return {
        'optimizing_function': fix_optimization_function(),
        'boundaries': [(-3, 3)],
        'no_dimensions': 1,
        'find_max': False,
        'seed': 235918
    }


@pytest.fixture
def fix_optimization_constraint_1():
    """
    With all x in the boundary, but value must larger/equal than -x^2 - 1.
    => x^4 + x^3 -3x^2 + 1 - (-x^2 - 1) >= 0
    => x^4 + x^3 -2x^2 + 2 >= 0
    """
    return lambda x: x[0] ** 4 + x[0] ** 3 - 2 * (x[0] ** 2) + 2 >= 0


@pytest.fixture
def fix_optimization_constraint_2():
    """
    With all x in the boundary, but value must lesser/equal than -x^2 + 0.9.
    => x^4 + x^3 -3x^2 + 1 - (-x^2 + 0.9) <= 0
    => x^4 + x^3 -2x^2 + 0.1 <= 0
    """
    return lambda x: x[0]**4 + x[0]**3 - 2*(x[0] ** 2) + 0.1 <= 0


@pytest.fixture
def fix_optimization_object():
    kwargs = fix_optimization_object_kwargs()
    opt_object = Optimization(**kwargs)
    opt_object.add_constraint(fix_optimization_constraint_1())
    opt_object.add_constraint(fix_optimization_constraint_2())
    return opt_object


@pytest.fixture
def fix_algorithm_object():
    algorithm_object = AlgorithmObject(fix_optimization_object())
    return algorithm_object
