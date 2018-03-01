from clustaar.schemas.v1 import STORE_SESSION_VALUE_ACTION
from clustaar.schemas.models import StoreSessionValueAction
import pytest


@pytest.fixture
def action():
    return StoreSessionValueAction(key="var1", value="val1")


@pytest.fixture
def data():
    return {
        "type": "store_session_value_action",
        "key": "var1",
        "value": "val1"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = STORE_SESSION_VALUE_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, STORE_SESSION_VALUE_ACTION)
        assert isinstance(action, StoreSessionValueAction)
        assert action.key == "var1"
        assert action.value == "val1"
