from elife_bus_sdk.exceptions import PublisherTypeNotFound, MessageQueueTypeNotFound
from elife_bus_sdk.publishers import EventPublisher, get_publisher_types
from elife_bus_sdk.queues import MessageQueue, get_queue_types


__version__ = '0.0.4'


DEFAULT_PUB_TYPE = 'sns'
PUBLISHER_TYPES = get_publisher_types()

DEFAULT_QUEUE_TYPE = 'sqs'
QUEUE_TYPES = get_queue_types()


def get_publisher(config: dict, pub_type: str = DEFAULT_PUB_TYPE) -> EventPublisher:
    """Publisher factory function.

    :param config: dict
    :param pub_type: str
    :return: :class: `EventPublisher`
    """
    publisher = PUBLISHER_TYPES.get(pub_type, None)

    if not publisher:
        raise PublisherTypeNotFound('Publisher type: {} was not found'.format(pub_type))

    return publisher(**config)


def get_queue(config: dict, q_type: str = DEFAULT_QUEUE_TYPE) -> MessageQueue:
    """MessageQueue factory function.

    :param config: dict
    :param q_type: str
    :return: :class: `MessageQueue`
    """

    queue = QUEUE_TYPES.get(q_type, None)

    if not queue:
        raise MessageQueueTypeNotFound('MessageQueue type: {} was not found'.format(q_type))

    return queue(**config)
