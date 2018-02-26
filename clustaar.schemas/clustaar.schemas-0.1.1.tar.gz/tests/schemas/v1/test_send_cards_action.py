from clustaar.schemas.v1 import SEND_CARDS_ACTIONS
from clustaar.schemas.models import ShareAction, Button, Card, SendCardsAction
import pytest


@pytest.fixture
def button():
    return Button(title="Share",
                  action=ShareAction())


@pytest.fixture
def card(button):
    return Card(title="Card 1",
                subtitle="xxx",
                image_url="http://example.com/logo.png",
                url="http://example.com",
                buttons=[button])


@pytest.fixture
def action(card):
    return SendCardsAction(cards=[card])


@pytest.fixture
def data(card):
    return {
        "type": "send_cards_action",
        "cards": [
            {
                "type": "card",
                "title": card.title,
                "subtitle": card.subtitle,
                "imageURL": card.image_url,
                "url": card.url,
                "buttons": [
                    {
                        "type": "button",
                        "title": "Share",
                        "action": {
                            "type": "share_action"
                        }
                    }
                ]
            }
        ]
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_CARDS_ACTIONS.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_CARDS_ACTIONS)
        assert isinstance(action, SendCardsAction)
        card = action.cards[0]
        assert card.title == "Card 1"
        assert card.subtitle == "xxx"
        assert card.image_url == "http://example.com/logo.png"
        assert card.url == "http://example.com"
        button = card.buttons[0]
        assert button.title == "Share"
        assert isinstance(button.action, ShareAction)
