from clustaar.schemas.v1 import SEND_QUICK_REPLIES_ACTION
from clustaar.schemas.models import GoToAction, QuickReply, SendQuickRepliesAction, StepTarget
import pytest


@pytest.fixture
def go_to_action():
    target = StepTarget(step_id="a1" * 12,
                        name="a step")
    return GoToAction(target=target)


@pytest.fixture
def quick_reply(go_to_action):
    return QuickReply(action=go_to_action,
                      title="Ok")


@pytest.fixture
def action(quick_reply):
    return SendQuickRepliesAction(message="Ok?",
                                  buttons=[quick_reply])


@pytest.fixture
def data():
    return {
        "type": "send_quick_replies_action",
        "message": "Ok?",
        "buttons": [
            {
                "type": "quick_reply",
                "title": "Ok",
                "action": {
                    "type": "go_to_action",
                    "target": {
                        "type": "step",
                        "name": "a step",
                        "id": "a1" * 12
                    }
                }
            }
        ]
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_QUICK_REPLIES_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_QUICK_REPLIES_ACTION)
        assert isinstance(action, SendQuickRepliesAction)
        assert action.message == "Ok?"
        quick_reply = action.buttons[0]
        assert quick_reply.title == "Ok"
        assert quick_reply.action.target.step_id == "a1" * 12
