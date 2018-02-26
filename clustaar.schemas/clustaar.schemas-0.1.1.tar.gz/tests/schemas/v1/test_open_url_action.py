from clustaar.schemas.v1 import OPEN_URL_ACTION
from clustaar.schemas.models import OpenURLAction
import pytest


@pytest.fixture
def action():
    return OpenURLAction(url="http://example.com")


@pytest.fixture
def data(action):
    return {
        "type": "open_url_action",
        "url": action.url
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = OPEN_URL_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, OPEN_URL_ACTION)
        assert isinstance(action, OpenURLAction)
        assert action.url == "http://example.com"
