from clustaar.schemas.v1 import WEBHOOK_REQUEST
from clustaar.schemas.models import Interlocutor, ConversationSession, Coordinates, Step,\
    PauseBotAction, StepReached, WebhookRequest
import pytest


@pytest.fixture
def action():
    return PauseBotAction()


@pytest.fixture
def step(action):
    return Step(actions=[action],
                name="A step",
                user_data="{}",
                id="1234")


@pytest.fixture
def interlocutor():
    location = Coordinates(lat=1.0, long=2.4)
    return Interlocutor(id="123", location=location)


@pytest.fixture
def session():
    return ConversationSession(values={"name": "tintin"})


@pytest.fixture
def request(step, session, interlocutor):
    event = StepReached(step=step,
                        session=session,
                        interlocutor=interlocutor,
                        channel="facebook")
    return WebhookRequest(event=event,
                          bot_id="4321",
                          timestamp=1514998709,
                          topic="conversation.step_reached")


@pytest.fixture
def data():
    return {
        "botID": "4321",
        "timestamp": 1514998709,
        "topic": "conversation.step_reached",
        "data": {
            "type": "step_reached_event",
            "channel": "facebook",
            "interlocutor": {
                "id": "123",
                "location": {
                    "lat": 1.0, "long": 2.4
                }
            },
            "session": {
                "values": {"name": "tintin"}
            },
            "step": {
                "actions": [
                    {
                        "type": "pause_bot_action"
                    }
                ],
                "id": "1234",
                "name": "A step",
                "userData": "{}"
            }
        }
    }


class TestDump(object):
    def test_returns_a_dict(self, request, mapper, data):
        result = WEBHOOK_REQUEST.dump(request, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_a_request(self, request, mapper, data):
        request = mapper.load(data, WEBHOOK_REQUEST)
        assert isinstance(request, WebhookRequest)
        assert isinstance(request.event, StepReached)
        assert request.event.step.id == "1234"
