from tree_decode.tests.utils import MockBuffer, mock_open
from sklearn.exceptions import NotFittedError

import tree_decode.utils as utils
import numpy as np
import pytest


class TestCheckEstimatorType(object):

    def test_supported(self, model):

        # Make sure no exception is raised.
        estimator = model()
        utils.check_model_type(estimator)

    def test_unsupported(self):
        match = "Function support is not implemented for"
        message = "Expected NotImplementedError regarding no support"

        with pytest.raises(NotImplementedError, match=match, message=message):
            utils.check_model_type([])


class TestCheckIsFitted(object):

    def test_fitted(self, tree):

        # Make sure no exception is raised.
        model = tree()
        model.tree_ = "tree_"
        utils.check_is_fitted(model)

    def test_unfitted(self, tree):
        match = "instance is not fitted yet"
        message = "Expected NotFittedError when checking"

        model = tree()

        with pytest.raises(NotFittedError, match=match, message=message):
            utils.check_is_fitted(model)

    def test_unsupported(self):
        match = "Function support is not implemented for"
        message = "Expected NotImplementedError regarding no support"

        with pytest.raises(NotImplementedError, match=match, message=message):
            utils.check_is_fitted([])


class TestExtractEstimators(object):

    def test_extract_single(self, tree):
        model = tree()
        expected = [model]

        result = utils.get_estimators(model)
        assert expected == result

    def test_extract_ensemble(self, ensemble):
        model = ensemble()
        model.estimators_ = [1, 2, 3]
        expected = model.estimators_[:]

        result = utils.get_estimators(model)
        assert expected == result

    def test_extract_unfitted_ensemble(self, ensemble):
        model = ensemble()

        match = ("The ensemble model needs to be fitted first "
                 "before estimators can be extracted")
        message = "Expected NotFittedError regarding unfitted ensemble model"

        with pytest.raises(NotFittedError, match=match, message=message):
            utils.get_estimators(model)

    def test_extract_unsupported(self):
        match = "Cannot extract estimators for"
        message = "Expected NotImplementedError regarding no support"

        with pytest.raises(NotImplementedError, match=match, message=message):
            utils.get_estimators([])


@pytest.mark.parametrize("tab_size", [-5, 0, 2, 5, None])
def test_get_tab(tab_size):
    tab_size = 5 if tab_size is None else max(0, tab_size)
    assert utils.get_tab(tab_size) == " " * tab_size


class TestGetTreeAt(object):

    @pytest.mark.parametrize("index", [0, 1])
    def test_get(self, index, ensemble):
        model = ensemble()
        model.estimators_ = [5, 6]
        assert utils.get_tree_at(model, index) == model.estimators_[index]

    def test_invalid(self):
        match = "This is not a valid tree ensemble model"
        message = "Expected TypeError because this object is of the wrong type"

        index = 0
        model = []

        with pytest.raises(TypeError, match=match, message=message):
            utils.get_tree_at(model, index)

    def test_out_of_bounds(self, ensemble):
        match = "There is no tree at index"
        message = "Expected IndexError because the index is out of bounds"

        index = 2
        model = ensemble()
        model.estimators_ = [5, 6]

        with pytest.raises(IndexError, match=match, message=message):
            utils.get_tree_at(model, index)

    def test_unfitted(self, ensemble):
        match = "This model has not been fitted yet"
        message = "Expected NotFittedError because the model is not fitted yet"

        index = 0
        model = ensemble()

        with pytest.raises(NotFittedError, match=match, message=message):
            utils.get_tree_at(model, index)


class TestMaybeRound(object):

    @pytest.mark.parametrize("precision,expected", [(None, 2.05),
                                                    (1, 2.0),
                                                    (5, 2.05)])
    def test_scalar(self, precision, expected):
        scalar = 2.05
        result = utils.maybe_round(scalar, precision=precision)

        assert result == expected

    @pytest.mark.parametrize("precision,expected", [(None, [2.05, 1.072, 3.6]),
                                                    (0, [2.0, 1.0, 4.0]),
                                                    (1, [2.0, 1.1, 3.6]),
                                                    (2, [2.05, 1.07, 3.6]),
                                                    (5, [2.05, 1.072, 3.6])])
    def test_array(self, precision, expected):
        expected = np.array(expected)
        arr = np.array([2.05, 1.072, 3.6])

        result = utils.maybe_round(arr, precision=precision)
        assert np.array_equal(result, expected)


class TestWriteToBuf(object):

    data = "example-data"
    filepath = "file-path.txt"

    def test_no_buf(self):
        # Nothing should happen here.
        utils.write_to_buf(self.data, filepath_or_buffer=None)

    def test_actual_buf(self):
        buffer = MockBuffer()
        utils.write_to_buf(self.data, filepath_or_buffer=buffer)

        # Because a buffer was provided, we preserve state
        # and do not close this buffer in this case.
        assert buffer.read() == self.data
        assert not buffer.closed

    @mock_open(data, filepath)
    def test_cat(self):
        utils.write_to_buf(self.data, filepath_or_buffer=self.filepath)
