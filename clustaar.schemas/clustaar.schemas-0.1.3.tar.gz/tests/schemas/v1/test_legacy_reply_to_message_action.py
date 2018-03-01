import pytest
from clustaar.schemas.v1 import LEGACY_REPLY_TO_MESSAGE_ACTION
from clustaar.schemas.models import LegacyReplyToMessageAction


@pytest.fixture
def action():
    return LegacyReplyToMessageAction(message="ok")


@pytest.fixture
def data(action):
    return {
        "type": "legacy_reply_to_message_action",
        "message": action.message
    }


class TestLoad(object):
    def test_loads_an_action(self, action, data, mapper):
        loaded_action = mapper.load(data, LEGACY_REPLY_TO_MESSAGE_ACTION)
        assert loaded_action.message == action.message


class TestDump(object):
    def test_dump_targs_into_dict(self, action, data, mapper):
        dump = LEGACY_REPLY_TO_MESSAGE_ACTION.dump(action, mapper)
        assert dump == data
