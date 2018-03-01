from clustaar.schemas.v1 import STEP_TARGET
from clustaar.schemas.models import StepTarget
import pytest


@pytest.fixture
def target():
    return StepTarget(name="a step", step_id="a1" * 12)


@pytest.fixture
def data():
    return {
        "type": "step",
        "name": "a step",
        "id": "a1" * 12
    }


class TestDump(object):
    def test_returns_a_dict(self, target, data, mapper):
        result = STEP_TARGET.dump(target, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_a_target(self, data, mapper):
        target = mapper.load(data, STEP_TARGET)
        assert isinstance(target, StepTarget)
        assert target.step_id == "a1" * 12
        assert target.name == "a step"
