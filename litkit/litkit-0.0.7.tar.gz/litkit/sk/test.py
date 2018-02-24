import unittest

from litkit.sk import list_estimators, list_regressors


class TestSk(unittest.TestCase):
    def test_list_estimators(self):
        list_estimators()

        list_regressors()