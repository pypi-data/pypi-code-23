from clustaar.schemas.v1 import SEND_EMAIL_ACTION
from clustaar.schemas.models import SendEmailAction
import pytest


@pytest.fixture
def action():
    return SendEmailAction(recipient="test@example.com",
                           subject="Hello",
                           content=":)")


@pytest.fixture
def data():
    return {
        "type": "send_email_action",
        "recipient": "test@example.com",
        "subject": "Hello",
        "content": ":)"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_EMAIL_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_EMAIL_ACTION)
        assert isinstance(action, SendEmailAction)
        assert action.content == ":)"
        assert action.subject == "Hello"
        assert action.recipient == "test@example.com"
