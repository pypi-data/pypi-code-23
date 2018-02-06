from tree_decode.tests.utils import load_model, MockBuffer
from sklearn.exceptions import NotFittedError

import tree_decode.api as api
import numpy as np
import pytest
import os


class BaseApiTest(object):

    min_args = ()

    @staticmethod
    def api_call(*args, **kwargs):
        raise NotImplementedError("API calling not implemented for base class")

    @staticmethod
    def load_model(filename):
        directory = os.path.dirname(__file__)
        directory = os.path.join(directory, "models")

        filename = os.path.join(directory, filename)
        return load_model(filename)

    @classmethod
    def setup_class(cls):
        cls.dtc_model = cls.load_model("dtc-model.pickle")
        cls.dtr_model = cls.load_model("dtr-model.pickle")
        cls.etc_model = cls.load_model("etc-model.pickle")
        cls.etr_model = cls.load_model("etr-model.pickle")

        cls.rfc_model = cls.load_model("rfc-model.pickle")
        cls.rfr_model = cls.load_model("rfr-model.pickle")
        cls.etsc_model = cls.load_model("etsc-model.pickle")
        cls.etsr_model = cls.load_model("etsr-model.pickle")

    def test_unsupported(self):
        match = "Function support is not implemented for"
        message = "Expected NotImplementedError regarding no support"

        with pytest.raises(NotImplementedError, match=match, message=message):
            self.api_call([], *self.min_args)

    def test_unfitted(self, tree):
        match = "instance is not fitted yet"
        message = "Expected NotFittedError regarding fitting"

        with pytest.raises(NotFittedError, match=match, message=message):
            self.api_call(tree(), *self.min_args)


class TestGetTreeInfo(BaseApiTest):

    min_args = ()

    @staticmethod
    def api_call(*args, **kwargs):
        return api.get_tree_info(*args, **kwargs)

    def test_basic(self):
        result = self.api_call(self.dtc_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
     node=1 left node: scores = [[1. 0. 0.]]

     node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
          node=3 left node: scores = [[0.    0.917 0.083]]
          node=4 left node: scores = [[0.    0.026 0.974]]
"""
        assert result == expected

        result = self.api_call(self.dtr_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 0 <= 3.133 else to node 4.
     node=1: go to node 2 if feature 0 <= 0.514 else to node 3.
          node=2 left node: scores = [[1.]]
          node=3 left node: scores = [[1.]]

     node=4: go to node 5 if feature 0 <= 3.85 else to node 6.
          node=5 left node: scores = [[-1.]]
          node=6 left node: scores = [[-1.]]
"""
        assert result == expected

        result = self.api_call(self.etc_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 0 <= 5.364 else to node 2.
     node=1 left node: scores = [[0.882 0.088 0.029]]

     node=2: go to node 3 if feature 3 <= 1.922 else to node 4.
          node=3 left node: scores = [[0.132 0.585 0.283]]
          node=4 left node: scores = [[0. 0. 1.]]
"""
        assert result == expected

        result = self.api_call(self.etr_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 2 <= 2.289 else to node 2.
     node=1 left node: scores = [[0.]]

     node=2: go to node 3 if feature 2 <= 5.029 else to node 4.
          node=3 left node: scores = [[1.]]
          node=4 left node: scores = [[1.]]
"""
        assert result == expected

        result = self.api_call(self.rfc_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 0 <= 5.45 else to node 6.
     node=1: go to node 2 if feature 2 <= 2.6 else to node 3.
          node=2 left node: scores = [[1. 0. 0.]]

          node=3: go to node 4 if feature 2 <= 4.0 else to node 5.
               node=4 left node: scores = [[0. 1. 0.]]
               node=5 left node: scores = [[0. 0. 1.]]

     node=6: go to node 7 if feature 0 <= 6.35 else to node 18.
          node=7: go to node 8 if feature 3 <= 1.7 else to node 13.
               node=8: go to node 9 if feature 0 <= 5.95 else to node 10.
                    node=9 left node: scores = [[0. 1. 0.]]

                    node=10: go to node 11 if feature 2 <= 4.95 else to node 12.
                         node=11 left node: scores = [[0. 1. 0.]]
                         node=12 left node: scores = [[0. 0. 1.]]

               node=13: go to node 14 if feature 0 <= 5.95 else to node 17.
                    node=14: go to node 15 if feature 1 <= 3.1 else to node 16.
                         node=15 left node: scores = [[0. 0. 1.]]
                         node=16 left node: scores = [[0. 1. 0.]]

                    node=17 left node: scores = [[0. 0. 1.]]

          node=18: go to node 19 if feature 2 <= 5.05 else to node 20.
               node=19 left node: scores = [[0. 1. 0.]]
               node=20 left node: scores = [[0. 0. 1.]]


Info for Decision Tree 1

node=0: go to node 1 if feature 2 <= 2.6 else to node 2.
     node=1 left node: scores = [[1. 0. 0.]]

     node=2: go to node 3 if feature 2 <= 4.85 else to node 4.
          node=3 left node: scores = [[0. 1. 0.]]

          node=4: go to node 5 if feature 1 <= 2.6 else to node 8.
               node=5: go to node 6 if feature 2 <= 4.95 else to node 7.
                    node=6 left node: scores = [[0. 1. 0.]]
                    node=7 left node: scores = [[0. 0. 1.]]

               node=8: go to node 9 if feature 3 <= 1.75 else to node 12.
                    node=9: go to node 10 if feature 1 <= 2.9 else to node 11.
                         node=10 left node: scores = [[0. 0. 1.]]
                         node=11 left node: scores = [[0. 1. 0.]]

                    node=12 left node: scores = [[0. 0. 1.]]
"""  # noqa
        assert result == expected

        result = self.api_call(self.rfr_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 2 <= 2.35 else to node 2.
     node=1 left node: scores = [[0.]]

     node=2: go to node 3 if feature 3 <= 1.75 else to node 8.
          node=3: go to node 4 if feature 2 <= 4.95 else to node 5.
               node=4 left node: scores = [[1.]]

               node=5: go to node 6 if feature 1 <= 2.6 else to node 7.
                    node=6 left node: scores = [[1.]]
                    node=7 left node: scores = [[1.]]

          node=8: go to node 9 if feature 2 <= 4.85 else to node 12.
               node=9: go to node 10 if feature 1 <= 3.1 else to node 11.
                    node=10 left node: scores = [[1.]]
                    node=11 left node: scores = [[1.]]

               node=12 left node: scores = [[1.]]


Info for Decision Tree 1

node=0: go to node 1 if feature 2 <= 4.7 else to node 4.
     node=1: go to node 2 if feature 2 <= 2.5 else to node 3.
          node=2 left node: scores = [[0.]]
          node=3 left node: scores = [[1.]]

     node=4: go to node 5 if feature 2 <= 4.95 else to node 8.
          node=5: go to node 6 if feature 2 <= 4.85 else to node 7.
               node=6 left node: scores = [[1.]]
               node=7 left node: scores = [[1.]]

          node=8 left node: scores = [[1.]]
"""
        assert result == expected

        result = self.api_call(self.etsc_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 1.793 else to node 26.
     node=1: go to node 2 if feature 0 <= 6.312 else to node 21.
          node=2: go to node 3 if feature 2 <= 5.074 else to node 20.
               node=3: go to node 4 if feature 2 <= 4.824 else to node 17.
                    node=4: go to node 5 if feature 0 <= 5.317 else to node 12.
                         node=5: go to node 6 if feature 2 <= 3.979 else to node 11.
                              node=6: go to node 7 if feature 3 <= 1.055 else to node 10.
                                   node=7: go to node 8 if feature 2 <= 1.979 else to node 9.
                                        node=8 left node: scores = [[1. 0. 0.]]
                                        node=9 left node: scores = [[0. 1. 0.]]

                                   node=10 left node: scores = [[0. 1. 0.]]

                              node=11 left node: scores = [[0. 0. 1.]]

                         node=12: go to node 13 if feature 1 <= 4.31 else to node 16.
                              node=13: go to node 14 if feature 3 <= 0.453 else to node 15.
                                   node=14 left node: scores = [[1. 0. 0.]]
                                   node=15 left node: scores = [[0. 1. 0.]]

                              node=16 left node: scores = [[1. 0. 0.]]

                    node=17: go to node 18 if feature 0 <= 6.056 else to node 19.
                         node=18 left node: scores = [[0. 0. 1.]]
                         node=19 left node: scores = [[0. 1. 0.]]

               node=20 left node: scores = [[0. 0. 1.]]

          node=21: go to node 22 if feature 0 <= 6.926 else to node 23.
               node=22 left node: scores = [[0. 1. 0.]]

               node=23: go to node 24 if feature 3 <= 1.556 else to node 25.
                    node=24 left node: scores = [[0. 1. 0.]]
                    node=25 left node: scores = [[0. 0. 1.]]

     node=26: go to node 27 if feature 3 <= 1.921 else to node 32.
          node=27: go to node 28 if feature 0 <= 6.269 else to node 31.
               node=28: go to node 29 if feature 1 <= 3.177 else to node 30.
                    node=29 left node: scores = [[0. 0. 1.]]
                    node=30 left node: scores = [[0. 1. 0.]]

               node=31 left node: scores = [[0. 0. 1.]]

          node=32 left node: scores = [[0. 0. 1.]]


Info for Decision Tree 1

node=0: go to node 1 if feature 3 <= 1.585 else to node 22.
     node=1: go to node 2 if feature 0 <= 5.195 else to node 9.
          node=2: go to node 3 if feature 1 <= 2.153 else to node 4.
               node=3 left node: scores = [[0. 1. 0.]]

               node=4: go to node 5 if feature 1 <= 3.795 else to node 8.
                    node=5: go to node 6 if feature 2 <= 1.878 else to node 7.
                         node=6 left node: scores = [[1. 0. 0.]]
                         node=7 left node: scores = [[0. 1. 0.]]

                    node=8 left node: scores = [[1. 0. 0.]]

          node=9: go to node 10 if feature 1 <= 3.025 else to node 19.
               node=10: go to node 11 if feature 3 <= 1.415 else to node 12.
                    node=11 left node: scores = [[0. 1. 0.]]

                    node=12: go to node 13 if feature 1 <= 2.435 else to node 16.
                         node=13: go to node 14 if feature 0 <= 6.145 else to node 15.
                              node=14 left node: scores = [[0. 0. 1.]]
                              node=15 left node: scores = [[0. 1. 0.]]

                         node=16: go to node 17 if feature 2 <= 4.991 else to node 18.
                              node=17 left node: scores = [[0. 1. 0.]]
                              node=18 left node: scores = [[0. 0. 1.]]

               node=19: go to node 20 if feature 2 <= 4.302 else to node 21.
                    node=20 left node: scores = [[1. 0. 0.]]
                    node=21 left node: scores = [[0. 1. 0.]]

     node=22: go to node 23 if feature 1 <= 2.741 else to node 24.
          node=23 left node: scores = [[0. 0. 1.]]

          node=24: go to node 25 if feature 2 <= 5.596 else to node 38.
               node=25: go to node 26 if feature 2 <= 4.688 else to node 27.
                    node=26 left node: scores = [[0. 1. 0.]]

                    node=27: go to node 28 if feature 2 <= 5.36 else to node 37.
                         node=28: go to node 29 if feature 1 <= 3.29 else to node 36.
                              node=29: go to node 30 if feature 2 <= 5.015 else to node 35.
                                   node=30: go to node 31 if feature 2 <= 4.83 else to node 34.
                                        node=31: go to node 32 if feature 0 <= 5.984 else to node 33.
                                             node=32 left node: scores = [[0. 1. 0.]]
                                             node=33 left node: scores = [[0. 0. 1.]]

                                        node=34 left node: scores = [[0. 1. 0.]]

                                   node=35 left node: scores = [[0. 0. 1.]]

                              node=36 left node: scores = [[0. 1. 0.]]

                         node=37 left node: scores = [[0. 0. 1.]]

               node=38 left node: scores = [[0. 0. 1.]]
"""  # noqa
        assert result == expected

        result = self.api_call(self.etsr_model)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 0 <= 6.073 else to node 16.
     node=1: go to node 2 if feature 1 <= 2.714 else to node 7.
          node=2: go to node 3 if feature 2 <= 4.339 else to node 6.
               node=3: go to node 4 if feature 0 <= 4.518 else to node 5.
                    node=4 left node: scores = [[0.]]
                    node=5 left node: scores = [[1.]]

               node=6 left node: scores = [[1.]]

          node=7: go to node 8 if feature 3 <= 0.97 else to node 9.
               node=8 left node: scores = [[0.]]

               node=9: go to node 10 if feature 2 <= 5.047 else to node 15.
                    node=10: go to node 11 if feature 2 <= 4.658 else to node 12.
                         node=11 left node: scores = [[1.]]

                         node=12: go to node 13 if feature 1 <= 3.098 else to node 14.
                              node=13 left node: scores = [[1.]]
                              node=14 left node: scores = [[1.]]

                    node=15 left node: scores = [[1.]]

     node=16: go to node 17 if feature 3 <= 1.571 else to node 20.
          node=17: go to node 18 if feature 2 <= 5.011 else to node 19.
               node=18 left node: scores = [[1.]]
               node=19 left node: scores = [[1.]]

          node=20: go to node 21 if feature 3 <= 1.893 else to node 28.
               node=21: go to node 22 if feature 3 <= 1.764 else to node 27.
                    node=22: go to node 23 if feature 0 <= 6.559 else to node 24.
                         node=23 left node: scores = [[1.]]

                         node=24: go to node 25 if feature 3 <= 1.66 else to node 26.
                              node=25 left node: scores = [[1.]]
                              node=26 left node: scores = [[1.]]

                    node=27 left node: scores = [[1.]]

               node=28 left node: scores = [[1.]]


Info for Decision Tree 1

node=0: go to node 1 if feature 3 <= 0.581 else to node 2.
     node=1 left node: scores = [[0.]]

     node=2: go to node 3 if feature 3 <= 1.335 else to node 6.
          node=3: go to node 4 if feature 1 <= 3.061 else to node 5.
               node=4 left node: scores = [[1.]]
               node=5 left node: scores = [[0.]]

          node=6: go to node 7 if feature 2 <= 5.113 else to node 26.
               node=7: go to node 8 if feature 2 <= 4.382 else to node 9.
                    node=8 left node: scores = [[1.]]

                    node=9: go to node 10 if feature 2 <= 4.713 else to node 13.
                         node=10: go to node 11 if feature 0 <= 5.211 else to node 12.
                              node=11 left node: scores = [[1.]]
                              node=12 left node: scores = [[1.]]

                         node=13: go to node 14 if feature 0 <= 6.653 else to node 23.
                              node=14: go to node 15 if feature 2 <= 5.076 else to node 22.
                                   node=15: go to node 16 if feature 2 <= 4.947 else to node 21.
                                        node=16: go to node 17 if feature 3 <= 1.622 else to node 18.
                                             node=17 left node: scores = [[1.]]

                                             node=18: go to node 19 if feature 1 <= 3.123 else to node 20.
                                                  node=19 left node: scores = [[1.]]
                                                  node=20 left node: scores = [[1.]]

                                        node=21 left node: scores = [[1.]]

                                   node=22 left node: scores = [[1.]]

                              node=23: go to node 24 if feature 2 <= 5.056 else to node 25.
                                   node=24 left node: scores = [[1.]]
                                   node=25 left node: scores = [[1.]]

               node=26 left node: scores = [[1.]]
"""  # noqa
        assert result == expected

    def test_names(self):
        names = {0: "Sepal Length", 1: "Sepal Width",
                 2: "Petal Length", 3: "Petal Width"}
        result = self.api_call(self.dtc_model, names=names)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if Petal Width <= 0.8 else to node 2.
     node=1 left node: scores = [[1. 0. 0.]]

     node=2: go to node 3 if Petal Length <= 4.95 else to node 4.
          node=3 left node: scores = [[0.    0.917 0.083]]
          node=4 left node: scores = [[0.    0.026 0.974]]
"""
        assert result == expected

    def test_precision(self):
        precision = 2
        result = self.api_call(self.dtc_model, precision=precision)

        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
     node=1 left node: scores = [[1. 0. 0.]]

     node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
          node=3 left node: scores = [[0.   0.92 0.08]]
          node=4 left node: scores = [[0.   0.03 0.97]]
"""
        assert result == expected

    def test_normalize(self):
        result = self.api_call(self.dtc_model, normalize=True)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
     node=1 left node: scores = [[1. 0. 0.]]

     node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
          node=3 left node: scores = [[0.    0.917 0.083]]
          node=4 left node: scores = [[0.    0.026 0.974]]
"""
        assert result == expected

        result = self.api_call(self.dtc_model, normalize=False)
        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
     node=1 left node: scores = [[37.  0.  0.]]

     node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
          node=3 left node: scores = [[ 0. 33.  3.]]
          node=4 left node: scores = [[ 0.  1. 38.]]
"""
        assert result == expected

    def test_label_index(self):
        label_index = 2
        result = self.api_call(self.dtc_model, label_index=label_index)

        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
     node=1 left node: score = 0.0

     node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
          node=3 left node: score = 0.083
          node=4 left node: score = 0.974
"""
        assert result == expected

        label_index = 10

        match = "is out of bounds on decision tree"
        message = "Expected IndexError regarding no support"

        with pytest.raises(IndexError, match=match, message=message):
            self.api_call(self.dtc_model, label_index=label_index)

    def test_tab_size(self):
        tab_size = 0
        result = self.api_call(self.dtc_model, tab_size=tab_size)

        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
node=1 left node: scores = [[1. 0. 0.]]

node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
node=3 left node: scores = [[0.    0.917 0.083]]
node=4 left node: scores = [[0.    0.026 0.974]]
"""
        assert result == expected

        tab_size = 2
        result = self.api_call(self.dtc_model, tab_size=tab_size)

        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
  node=1 left node: scores = [[1. 0. 0.]]

  node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
    node=3 left node: scores = [[0.    0.917 0.083]]
    node=4 left node: scores = [[0.    0.026 0.974]]
"""
        assert result == expected

    def test_buffer(self):
        buffer = MockBuffer()
        result = self.api_call(self.dtc_model, filepath_or_buffer=buffer)

        expected = """\


Info for Decision Tree 0

node=0: go to node 1 if feature 3 <= 0.8 else to node 2.
     node=1 left node: scores = [[1. 0. 0.]]

     node=2: go to node 3 if feature 2 <= 4.95 else to node 4.
          node=3 left node: scores = [[0.    0.917 0.083]]
          node=4 left node: scores = [[0.    0.026 0.974]]
"""
        # We wrote to a buffer, so the result
        # is not returned to the user.
        assert result is None
        assert buffer.read() == expected


class TestGetDecisionInfo(BaseApiTest):

    min_args = (np.array([]),)

    dtr_data = np.array([[5.8]])
    dtc_data = np.array([[5.8, 2.8, 5.1, 2.4]])
    etc_data = np.array([[5.8, 2.8, 5.1, 2.4]])
    etr_data = np.array([[5.8, 2.8, 5.1, 2.4]])

    rfc_data = np.array([[5.8, 2.8, 5.1, 2.4]])
    rfr_data = np.array([[5.8, 2.8, 5.1, 2.4]])
    etsc_data = np.array([[5.8, 2.8, 5.1, 2.4]])
    etsr_data = np.array([[5.8, 2.8, 5.1, 2.4]])

    @staticmethod
    def api_call(*args, **kwargs):
        return api.get_decision_info(*args, **kwargs)

    def test_basic(self):
        result = self.api_call(self.dtc_model, self.dtc_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 3 Score = 2.4 > 0.8
     Decision ID Node 2 : Feature 2 Score = 5.1 > 4.95
     Decision ID Node 4 : Scores = [0.    0.026 0.974]
"""
        assert result == expected

        result = self.api_call(self.dtr_model, self.dtr_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 0 Score = 5.8 > 3.133
     Decision ID Node 4 : Feature 0 Score = 5.8 > 3.85
     Decision ID Node 6 : Scores = [-0.869]
"""
        assert result == expected

        result = self.api_call(self.etc_model, self.etc_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 0 Score = 5.8 > 5.364
     Decision ID Node 2 : Feature 3 Score = 2.4 > 1.922
     Decision ID Node 4 : Scores = [0. 0. 1.]
"""
        assert result == expected

        result = self.api_call(self.etr_model, self.etr_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 2 Score = 5.1 > 2.289
     Decision ID Node 2 : Feature 2 Score = 5.1 > 5.029
     Decision ID Node 4 : Scores = [2.]
"""
        assert result == expected

        result = self.api_call(self.rfc_model, self.rfc_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 0 Score = 5.8 > 5.45
     Decision ID Node 6 : Feature 0 Score = 5.8 <= 6.35
     Decision ID Node 7 : Feature 3 Score = 2.4 > 1.7
     Decision ID Node 13 : Feature 0 Score = 5.8 <= 5.95
     Decision ID Node 14 : Feature 1 Score = 2.8 <= 3.1
     Decision ID Node 15 : Scores = [0. 0. 1.]

Decision Path for Tree 1:
     Decision ID Node 0 : Feature 2 Score = 5.1 > 2.6
     Decision ID Node 2 : Feature 2 Score = 5.1 > 4.85
     Decision ID Node 4 : Feature 1 Score = 2.8 > 2.6
     Decision ID Node 8 : Feature 3 Score = 2.4 > 1.75
     Decision ID Node 12 : Scores = [0. 0. 1.]
"""
        assert result == expected

        result = self.api_call(self.rfr_model, self.rfr_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 2 Score = 5.1 > 2.35
     Decision ID Node 2 : Feature 3 Score = 2.4 > 1.75
     Decision ID Node 8 : Feature 2 Score = 5.1 > 4.85
     Decision ID Node 12 : Scores = [2.]

Decision Path for Tree 1:
     Decision ID Node 0 : Feature 2 Score = 5.1 > 4.7
     Decision ID Node 4 : Feature 2 Score = 5.1 > 4.95
     Decision ID Node 8 : Scores = [2.]
"""
        assert result == expected

        result = self.api_call(self.etsc_model, self.etsc_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 3 Score = 2.4 > 1.793
     Decision ID Node 26 : Feature 3 Score = 2.4 > 1.921
     Decision ID Node 32 : Scores = [0. 0. 1.]

Decision Path for Tree 1:
     Decision ID Node 0 : Feature 3 Score = 2.4 > 1.585
     Decision ID Node 22 : Feature 1 Score = 2.8 > 2.741
     Decision ID Node 24 : Feature 2 Score = 5.1 <= 5.596
     Decision ID Node 25 : Feature 2 Score = 5.1 > 4.688
     Decision ID Node 27 : Feature 2 Score = 5.1 <= 5.36
     Decision ID Node 28 : Feature 1 Score = 2.8 <= 3.29
     Decision ID Node 29 : Feature 2 Score = 5.1 > 5.015
     Decision ID Node 35 : Scores = [0. 0. 1.]
"""
        assert result == expected

        result = self.api_call(self.etsr_model, self.etsr_data)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 0 Score = 5.8 <= 6.073
     Decision ID Node 1 : Feature 1 Score = 2.8 > 2.714
     Decision ID Node 7 : Feature 3 Score = 2.4 > 0.97
     Decision ID Node 9 : Feature 2 Score = 5.1 > 5.047
     Decision ID Node 15 : Scores = [2.]

Decision Path for Tree 1:
     Decision ID Node 0 : Feature 3 Score = 2.4 > 0.581
     Decision ID Node 2 : Feature 3 Score = 2.4 > 1.335
     Decision ID Node 6 : Feature 2 Score = 5.1 <= 5.113
     Decision ID Node 7 : Feature 2 Score = 5.1 > 4.382
     Decision ID Node 9 : Feature 2 Score = 5.1 > 4.713
     Decision ID Node 13 : Feature 0 Score = 5.8 <= 6.653
     Decision ID Node 14 : Feature 2 Score = 5.1 > 5.076
     Decision ID Node 22 : Scores = [2.]
"""
        assert result == expected

    def test_precision(self):
        precision = 2
        result = self.api_call(self.dtc_model, self.dtc_data,
                               precision=precision)

        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 3 Score = 2.4 > 0.8
     Decision ID Node 2 : Feature 2 Score = 5.1 > 4.95
     Decision ID Node 4 : Scores = [0.   0.03 0.97]
"""
        assert result == expected

    def test_names(self):
        names = {0: "Sepal Length", 1: "Sepal Width",
                 2: "Petal Length", 3: "Petal Width"}
        result = self.api_call(self.dtc_model, self.dtc_data, names=names)
        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Petal Width = 2.4 > 0.8
     Decision ID Node 2 : Petal Length = 5.1 > 4.95
     Decision ID Node 4 : Scores = [0.    0.026 0.974]
"""
        assert result == expected

    def test_label_index(self):
        label_index = 2
        result = self.api_call(self.dtc_model, self.dtc_data,
                               label_index=label_index)

        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 3 Score = 2.4 > 0.8
     Decision ID Node 2 : Feature 2 Score = 5.1 > 4.95
     Decision ID Node 4 : Scores = 0.974
"""
        assert result == expected

        label_index = 10

        match = "is out of bounds on decision tree"
        message = "Expected IndexError regarding no support"

        with pytest.raises(IndexError, match=match, message=message):
            self.api_call(self.dtc_model, self.dtc_data,
                          label_index=label_index)

    def test_tab_size(self):
        tab_size = 0
        result = self.api_call(self.dtc_model, self.dtc_data,
                               tab_size=tab_size)

        expected = """\

Decision Path for Tree 0:
Decision ID Node 0 : Feature 3 Score = 2.4 > 0.8
Decision ID Node 2 : Feature 2 Score = 5.1 > 4.95
Decision ID Node 4 : Scores = [0.    0.026 0.974]
"""
        assert result == expected

        tab_size = 2
        result = self.api_call(self.dtc_model, self.dtc_data,
                               tab_size=tab_size)

        expected = """\

Decision Path for Tree 0:
  Decision ID Node 0 : Feature 3 Score = 2.4 > 0.8
  Decision ID Node 2 : Feature 2 Score = 5.1 > 4.95
  Decision ID Node 4 : Scores = [0.    0.026 0.974]
"""
        assert result == expected

    def test_buffer(self):
        buffer = MockBuffer()
        result = self.api_call(self.dtc_model, self.dtc_data,
                               filepath_or_buffer=buffer)

        expected = """\

Decision Path for Tree 0:
     Decision ID Node 0 : Feature 3 Score = 2.4 > 0.8
     Decision ID Node 2 : Feature 2 Score = 5.1 > 4.95
     Decision ID Node 4 : Scores = [0.    0.026 0.974]
"""
        # We wrote to a buffer, so the result
        # is not returned to the user.
        assert result is None
        assert buffer.read() == expected
