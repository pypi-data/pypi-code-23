from elife_bus_sdk.publishers import (
    EventPublisher,
    get_publisher_types
)


__version__ = '0.0.3'


DEFAULT_NAME = 'default_publisher'
DEFAULT_TYPE = 'sns'
PUBLISHERS = {}
PUBLISHER_TYPES = get_publisher_types()


def get_publisher(config: dict, pub_name: str = DEFAULT_NAME,
                  pub_type: str = DEFAULT_TYPE) -> EventPublisher:
    """
    Publisher factory function.

    If a publisher already exists with the `pub_name` value
    then you will be returned that instance, otherwise the publisher
    will be created and returned.

    :param config: dict
    :param pub_name: str
    :param pub_type: str
    :return: :class: `EventPublisher`
    """
    if not PUBLISHERS.get(pub_name, None):
        if not pub_type:
            raise AttributeError('`pub_type` is a required argument for uninitialized PUBLISHERS')

        PUBLISHERS[pub_name] = PUBLISHER_TYPES[pub_type](**config)

    return PUBLISHERS[pub_name]
