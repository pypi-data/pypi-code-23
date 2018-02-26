from clustaar.schemas.v1 import SHARE_ACTION
from clustaar.schemas.models import ShareAction
import pytest


@pytest.fixture
def action():
    return ShareAction()


@pytest.fixture
def data(action):
    return {
        "type": "share_action"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SHARE_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SHARE_ACTION)
        assert isinstance(action, ShareAction)
