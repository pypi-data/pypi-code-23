import pytest

from elife_bus_sdk.events import ProfileEvent
from elife_bus_sdk.publishers import SNSPublisher


def test_it_will_create_arn_with_if_config_is_valid(sns_publisher: SNSPublisher):
    assert sns_publisher.arn == 'arn:aws:sns:local:00000000000:test-topic--dev'


def test_it_will_fail_to_publish_an_invalid_event(sns_publisher: SNSPublisher):
    event = {'invlaid': 'data'}
    with pytest.raises(AttributeError):
        sns_publisher.publish(event=event)


def test_it_will_publish_a_valid_event(sns_publisher: SNSPublisher):
    event = ProfileEvent(id='12345')
    assert sns_publisher.publish(event=event)


def test_it_will_raise_error_if_passed_invalid_event_type(sns_publisher: SNSPublisher):
    event = 'invalid_type'
    with pytest.raises(AttributeError):
        sns_publisher.publish(event=event)
