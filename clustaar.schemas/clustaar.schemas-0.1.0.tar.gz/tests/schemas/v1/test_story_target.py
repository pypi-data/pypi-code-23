import pytest
from clustaar.schemas.v1 import STORY_TARGET
from clustaar.schemas.models import StoryTarget


@pytest.fixture
def target():
    return StoryTarget(name="a story", story_id="a1" * 12)


@pytest.fixture
def data():
    return {
        "type": "story",
        "name": "a story",
        "id": "a1" * 12
    }


class TestDump(object):
    def test_returns_a_dict(self, target, data, mapper):
        result = STORY_TARGET.dump(target, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_a_target(self, data, mapper):
        target = mapper.load(data, STORY_TARGET)
        assert isinstance(target, StoryTarget)
        assert target.story_id == "a1" * 12
        assert target.name == "a story"
