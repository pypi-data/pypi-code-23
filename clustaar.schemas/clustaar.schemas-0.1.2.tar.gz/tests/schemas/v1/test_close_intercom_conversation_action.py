from clustaar.schemas.v1 import CLOSE_INTERCOM_CONVERSATION_ACTION
from clustaar.schemas.models import CloseIntercomConversationAction
import pytest


@pytest.fixture
def action():
    return CloseIntercomConversationAction()


@pytest.fixture
def data():
    return {
        "type": "close_intercom_conversation_action"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = CLOSE_INTERCOM_CONVERSATION_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, CLOSE_INTERCOM_CONVERSATION_ACTION)
        assert isinstance(action, CloseIntercomConversationAction)
