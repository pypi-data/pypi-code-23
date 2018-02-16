from unittest.mock import patch

from elife_bus_sdk import get_publisher
from elife_bus_sdk.publishers import SNSPublisher


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
def test_it_will_receive_default_name_if_name_is_not_supplied(valid_config):
    publisher = get_publisher(pub_type='sns', config=valid_config)
    publisher2 = get_publisher(pub_name='default_publisher', config=valid_config)
    assert publisher is publisher2


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
def test_it_will_receive_default_type_if_type_is_not_supplied(valid_config):
    publisher = get_publisher(pub_name='test1', config=valid_config)
    assert isinstance(publisher, SNSPublisher)


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
def test_it_returns_publisher_instance_when_given_valid_type(valid_config):
    publisher = get_publisher(pub_name='test1', pub_type='sns', config=valid_config)
    assert isinstance(publisher, SNSPublisher)
