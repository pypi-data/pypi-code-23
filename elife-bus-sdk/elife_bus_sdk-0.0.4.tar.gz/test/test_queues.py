from unittest.mock import patch, MagicMock
from typing import Dict

import pytest

from elife_bus_sdk import get_queue
from elife_bus_sdk.exceptions import MessageQueueTypeNotFound
from elife_bus_sdk.queues import get_queue_types, SQSMessageQueue


@patch('elife_bus_sdk.queues.sqs_queue.boto3')
# pylint:disable=unused-argument
def test_can_get_queue(mock_boto: MagicMock, valid_sqs_config: Dict[str, str]):
    assert get_queue(q_type='sqs', config=valid_sqs_config)


def test_it_raises_exception_for_unitialized_queue_type():
    with pytest.raises(MessageQueueTypeNotFound):
        get_queue(q_type='', config={})


def test_it_will_have_valid_queue_types_on_init():
    assert len(get_queue_types()) == 1


def test_children_of_message_queue_get_registered_by_name():
    queue_types = get_queue_types()

    assert queue_types['sqs'] == SQSMessageQueue
