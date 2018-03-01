from clustaar.schemas.v1 import PAUSE_BOT_ACTION
from clustaar.schemas.models import PauseBotAction
import pytest


@pytest.fixture
def action():
    return PauseBotAction()


@pytest.fixture
def data():
    return {
        "type": "pause_bot_action"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = PAUSE_BOT_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, PAUSE_BOT_ACTION)
        assert isinstance(action, PauseBotAction)
