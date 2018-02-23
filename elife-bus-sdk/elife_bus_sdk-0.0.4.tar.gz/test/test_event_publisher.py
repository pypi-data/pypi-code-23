from typing import Dict
from unittest.mock import patch, MagicMock

from elife_bus_sdk import get_publisher
from elife_bus_sdk.publishers import SNSPublisher


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
# pylint:disable=unused-argument
def test_it_will_receive_default_type_if_type_is_not_supplied(mock_boto: MagicMock,
                                                              valid_config: Dict[str, str]):
    publisher = get_publisher(config=valid_config)
    assert isinstance(publisher, SNSPublisher)


@patch('elife_bus_sdk.publishers.sns_publisher.boto3')
# pylint:disable=unused-argument
def test_it_returns_publisher_instance_when_given_valid_type(mock_boto: MagicMock,
                                                             valid_config: Dict[str, str]):
    publisher = get_publisher(pub_type='sns', config=valid_config)
    assert isinstance(publisher, SNSPublisher)
