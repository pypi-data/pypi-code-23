from .betterconfigclient import BetterConfigClient
from .interfaces import BetterConfigClientException
from .readwritelock import ReadWriteLock

__client = None
__lock = ReadWriteLock()


def initialize(project_secret,
               time_to_live_seconds=60,
               config_store_class=None):
    """
    Initializes the BetterConfigClient. If the client is already initialized it does nothing
    :param project_secret: The Project's Project secret
    :param time_to_live_seconds: TTL for the cache
    :param config_store_class: Customizable ConfigStore caching provider
    """
    global __client
    global __lock

    if __client:
        return

    try:
        __lock.acquire_write()

        if __client:
            return

        __client = BetterConfigClient(project_secret, time_to_live_seconds, config_store_class)
    finally:
        __lock.release_write()


def get():
    """
    Gets the initialized BetterConfigClient.
    In case you haven't called initialize before it raises a BetterConfigClientException.
    :return: The initialized BetterConfigClient.
    """
    global __client
    global __lock

    try:
        __lock.acquire_read()
        if __client:
            return __client
    finally:
        __lock.release_read()

    raise BetterConfigClientException("Initialize should be called before using BetterConfigClient")


def close():
    """
    Closes all resources
    """
    global __client
    global __lock

    try:
        __lock.acquire_write()

        if __client:
            __client.close()

        __client = None
    finally:
        __lock.release_write()
