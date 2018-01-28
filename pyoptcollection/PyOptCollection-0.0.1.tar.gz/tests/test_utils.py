"""Test py_opt_collection.utils module."""

from py_opt_collection.utils import is_better


def test_is_better():
    """
    Test utils.is_better() function.

    Scenarios:
    - Original value is None
    - Check if comparing value is greater than original value
    - Check if comparing value is smaller than original value
    """

    # None
    comparing_values = [1, 1.0]
    is_greater_values = [True, False]
    for i in comparing_values:
        for j in is_greater_values:
            assert is_better(None, i, j)

    # Greater than
    ori_values = [1, 1.0]
    greater_comparing_values = [2, 2.0]
    lesser_equal_comparing_values = [0, 0.5, 1, 1.0]
    for i in ori_values:
        for j in greater_comparing_values:
            assert is_better(i, j, True)
        for j in lesser_equal_comparing_values:
            assert not is_better(i, j, True)

    # Lesser than
    ori_values = [2, 2.0]
    lesser_comparing_values = [1, 1.0]
    greater_equal_comparing_values = [3, 2.5, 2, 2.0]
    for i in ori_values:
        for j in lesser_comparing_values:
            assert is_better(i, j, False)
        for j in greater_equal_comparing_values:
            assert not is_better(i, j, False)
