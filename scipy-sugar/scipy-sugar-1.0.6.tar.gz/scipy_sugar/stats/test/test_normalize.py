import scipy
from numpy.testing import assert_allclose


def test_quantile_gaussianize():
    from scipy_sugar.stats import quantile_gaussianize

    x = [
        1.76405235, 0.40015721, 0.97873798, 2.2408932, 1.86755799, -0.97727788,
        0.95008842, -0.15135721, -0.10321885, 0.4105985
    ]

    y = [
        0.6045853465832371, -0.3487556955170447, 0.3487556955170447,
        1.335177736118937, 0.9084578685373851, -1.3351777361189363,
        0.1141852943214284, -0.9084578685373853, -0.6045853465832371,
        -0.1141852943214282
    ]

    assert_allclose(quantile_gaussianize(x), y)


def test_quantile_gaussianize_unique():
    from scipy_sugar.stats import quantile_gaussianize

    x = [1, 1, 1, 1]
    y = [0, 0, 0, 0]
    assert_allclose(quantile_gaussianize(x), y)


def test_quantile_gaussianize_empty():
    from scipy_sugar.stats import quantile_gaussianize

    x = []
    y = []
    assert_allclose(quantile_gaussianize(x), y)


if __name__ == '__main__':
    __import__('pytest').main([__file__, '-s'])
