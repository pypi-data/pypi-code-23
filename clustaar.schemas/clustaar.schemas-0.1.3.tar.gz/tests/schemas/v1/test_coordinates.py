import pytest
from unittest.mock import Mock
from clustaar.schemas.v1 import COORDINATES


@pytest.fixture
def coordinates():
    return Mock(lat=1.0, long=2.4)


@pytest.fixture
def data():
    return {
        "lat": 1.0,
        "long": 2.4
    }


class TestDump(object):
    def test_returns_a_dict(self, data, coordinates):
        result = COORDINATES.dump(coordinates, mapper=None)
        assert result == data


class TestLoadAttrs(object):
    def test_returns_a_dict(self, data):
        coordinates = COORDINATES.load_attrs(data, mapper=None)
        assert coordinates == data
