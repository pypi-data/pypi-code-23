from clustaar.schemas.v1 import WAIT_ACTION
from clustaar.schemas.models import WaitAction
import pytest


@pytest.fixture
def action():
    return WaitAction(duration=2.3)


@pytest.fixture
def data():
    return {
        "type": "wait_action",
        "duration": 2.3
    }


class TestDump(object):
    def test_returns_a_dict(self, action, mapper, data):
        result = WAIT_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, WAIT_ACTION)
        assert isinstance(action, WaitAction)
        assert action.duration == 2.3
