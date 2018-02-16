from unittest.mock import patch

import pytest

from elife_bus_sdk.events import ProfileEvent
from elife_bus_sdk.publishers import SNSPublisher


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
def test_it_will_create_arn_with_if_config_is_valid(dev_config_overrides, valid_config):
    publisher = SNSPublisher(**valid_config, **dev_config_overrides)
    assert publisher.arn == 'arn:aws:sns:local:00000000000:test-topic--dev'


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
def test_it_will_fail_to_publish_an_invalid_event(dev_config_overrides, valid_config):
    event = {'invlaid': 'data'}
    publisher = SNSPublisher(**valid_config, **dev_config_overrides)
    with pytest.raises(AttributeError):
        publisher.publish(event=event)


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
def test_it_will_publish_a_valid_event(mock_boto, dev_config_overrides, valid_config):
    mock_boto.resource.Topic.publish.return_value = {}

    event = ProfileEvent(id='12345')
    publisher = SNSPublisher(**valid_config, **dev_config_overrides)
    assert publisher.publish(event=event)


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
def test_it_will_raise_error_if_passed_invalid_event_type(dev_config_overrides, valid_config):
    event = 'invalid_type'
    publisher = SNSPublisher(**valid_config, **dev_config_overrides)
    with pytest.raises(AttributeError):
        publisher.publish(event=event)
