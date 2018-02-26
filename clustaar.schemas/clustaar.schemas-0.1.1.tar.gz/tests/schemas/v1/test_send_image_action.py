from clustaar.schemas.v1 import SEND_IMAGE_ACTION
from clustaar.schemas.models import SendImageAction
import pytest


@pytest.fixture
def action():
    return SendImageAction(image_url="http://example.com/logo.png")


@pytest.fixture
def data():
    return {
        "type": "send_image_action",
        "url": "http://example.com/logo.png"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_IMAGE_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_IMAGE_ACTION)
        assert isinstance(action, SendImageAction)
        assert action.image_url == "http://example.com/logo.png"
