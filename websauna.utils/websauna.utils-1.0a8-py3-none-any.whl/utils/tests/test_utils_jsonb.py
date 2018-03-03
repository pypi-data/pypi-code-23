"""Test utils.jsonb."""
# Standard Library
from unittest import mock

import pytest

from websauna.utils import jsonb


@mock.patch("websauna.utils.jsonb._sqlalchemy_present", False)
def test_is_index_property_raises_on_no_sqlalchemy():
    """On no sqlalchemy, calling `is_index_property` should raise RuntimeError."""
    with pytest.raises(RuntimeError):
        jsonb.is_index_property(obj=object(), name="")


class MockIndexProperty:
    pass


class MockObj:
    mock_property = MockIndexProperty()
    other_property = object()


@mock.patch("websauna.utils.jsonb._sqlalchemy_present", True)
def test_is_index_property_works():
    """If sqlalchemy is present,  `is_index_property` should identify it properly."""
    if not hasattr(jsonb, "index_property"):
        jsonb.index_property = None
    with mock.patch("websauna.utils.jsonb.index_property", MockIndexProperty):
        assert jsonb.is_index_property(obj=MockObj(), name="mock_property")
        assert not jsonb.is_index_property(obj=MockObj(), name="other_property")
