
import unittest
import copy
import numpy as np

from .. import EM
from ...datasets import load_data


class TestEMMethods(unittest.TestCase):

    def test_parameter(self):
        X,_ = load_data.load_boston()
        self.assertIsNotNone(EM._init_parameters(self,X))

    def test_solve(self):
        X,_ = load_data.load_boston()
        imputed = EM().solve(X)
        self.assertIsNotNone(imputed)




if __name__ == '__main__':
    unittest.main()

