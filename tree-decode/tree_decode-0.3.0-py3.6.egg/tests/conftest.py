from sklearn.tree import (DecisionTreeClassifier, DecisionTreeRegressor,
                          ExtraTreeClassifier, ExtraTreeRegressor)
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor,
                              ExtraTreesClassifier, ExtraTreesRegressor)

import pytest


_SUPPORTED_TREES = (DecisionTreeClassifier, DecisionTreeRegressor,
                    ExtraTreeClassifier, ExtraTreeRegressor)
_SUPPORTED_ENSEMBLES = (RandomForestClassifier, RandomForestRegressor,
                        ExtraTreesClassifier, ExtraTreesRegressor)
_SUPPORTED = _SUPPORTED_TREES + _SUPPORTED_ENSEMBLES


@pytest.fixture(params=_SUPPORTED_TREES)
def tree(request):
    """
    Fixture for all supported decision tree classes to test.
    """

    return request.param


@pytest.fixture(params=_SUPPORTED_ENSEMBLES)
def ensemble(request):
    """
    Fixture for all supported ensemble decision tree classes to test.
    """

    return request.param


@pytest.fixture(params=_SUPPORTED)
def model(request):
    """
    Fixture for all supported (ensemble) decision tree classes to test.
    """

    return request.param
