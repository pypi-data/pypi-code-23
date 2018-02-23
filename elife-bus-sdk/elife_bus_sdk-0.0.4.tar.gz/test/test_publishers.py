import pytest

from elife_bus_sdk import get_publisher
from elife_bus_sdk.exceptions import PublisherTypeNotFound
from elife_bus_sdk.publishers import get_publisher_types, SNSPublisher


def test_it_raises_exception_for_unitialized_publisher_type():
    with pytest.raises(PublisherTypeNotFound):
        get_publisher(pub_type='', config={})


def test_it_will_have_valid_publisher_types_on_init():
    assert len(get_publisher_types()) == 1


def test_children_of_event_publisher_get_registered_by_name():
    publisher_types = get_publisher_types()

    assert publisher_types['sns'] == SNSPublisher
