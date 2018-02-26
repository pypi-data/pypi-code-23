from clustaar.schemas.v1 import SEND_TEXT_ACTION
from clustaar.schemas.models import SendTextAction
import pytest


@pytest.fixture
def action():
    return SendTextAction(alternatives=["Hi", "Hello"])


@pytest.fixture
def data():
    return {
        "type": "send_text_action",
        "alternatives": ["Hi", "Hello"]
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_TEXT_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_TEXT_ACTION)
        assert isinstance(action, SendTextAction)
        assert action.alternatives == ["Hi", "Hello"]
