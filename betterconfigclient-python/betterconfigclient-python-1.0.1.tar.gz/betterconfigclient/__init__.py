from betterconfigclient.betterconfigclient import BetterConfigClient
from betterconfigclient.interfaces import BetterConfigClientException
from betterconfigclient.readwritelock import ReadWriteLock

__client = None
__lock = ReadWriteLock()


def initialize(project_secret,
               time_to_leave_seconds=60,
               config_store_class=None):
    """
    Initializes the BetterConfigClient. If the client is already initialized it does nothing
    :param project_secret: The Project's Project secret
    :param time_to_leave_seconds: TTL for the cache
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

        __client = BetterConfigClient(project_secret, time_to_leave_seconds, config_store_class)
    finally:
        __lock.release_write()


def get():
    """
    Gets the initialized BetterConfigClient. In case you haven't called initialize before it raises a BetterConfigClientException.
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

    try:
        __lock.acquire_write()
        if not __client:
            raise BetterConfigClientException("Initialize should be called before using BetterConfigClient")
        return __client
    finally:
        __lock.unlock()
