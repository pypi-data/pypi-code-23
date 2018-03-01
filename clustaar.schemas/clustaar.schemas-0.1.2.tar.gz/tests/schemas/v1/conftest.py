import pytest
from lupin import constructor
from clustaar.schemas import v1


@pytest.fixture
def mapper():
    return v1.get_mapper(factory=constructor)
