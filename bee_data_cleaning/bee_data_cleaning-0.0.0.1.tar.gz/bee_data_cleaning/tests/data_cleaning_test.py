from unittest import TestCase
import pandas as pd
import bee_data_cleaning as dc
import numpy as np
import random
import numpy.testing as npt

class TestDataCleaning(TestCase):
    def calculate_znorm_equal_global_test(self):
        series = pd.Series([3]*5)
        znorm = dc.calculate_znorm(series)
        self.assertTrue(np.isnan(znorm).all())

    def calculate_znorm_equal_rolling_test(self):
        series = pd.Series([3]*5)
        znorm = dc.calculate_znorm(series, mode="rolling", window=3)
        self.assertTrue(np.isnan(znorm).all())

    def calculate_znorm_rolling_test(self):
        series = pd.Series([31, 0, 81, 55, 26, 23, 9, 76, 73, 4])
        result = np.array([ 1.,  1.11877003,  1.05625256,  0.04451411,  0.60060446,
        0.4949134 ,  0.93568178,  0.75509286,  0.66152326,  1.])
        znorm = dc.calculate_znorm(series, mode="rolling", window=3)
        npt.assert_almost_equal(znorm, result)

    def calculate_znorm_global_test(self):
        series = pd.Series([31, 0, 81, 55, 26, 23, 9, 76, 73, 4])
        result = np.array([ 0.23099873,  1.28408118,  1.46752135,  0.58429091,  0.40085074,
        0.50276194,  0.97834757,  1.29766934,  1.19575814,  1.14819957])
        znorm = dc.calculate_znorm(series)
        npt.assert_almost_equal(znorm, result)

    def detect_znorm_outliers_test(self):
        series = pd.Series([31, 0, 81, 55, 26, 23, 9, 76, 73, 4])
        outliers = dc.detect_znorm_outliers(series, 2)
        self.assertFalse(outliers.all())
        series[4] = 500
        outliers = dc.detect_znorm_outliers(series, 2)
        self.assertTrue(outliers[4])