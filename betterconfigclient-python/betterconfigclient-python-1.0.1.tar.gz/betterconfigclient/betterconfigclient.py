from betterconfigclient.configfetcher import CacheControlConfigFetcher
from betterconfigclient.configstore import InMemoryConfigStore


class BetterConfigClient(object):
    """
     A client for handling configurations provided by BetterConfig.
    """

    def __init__(self,
                 project_secret,
                 time_to_leave_seconds=60,
                 config_store_class=None):
        """
        Initializes the BetterConfigClient
        :param project_secret: The Project's Project secret
        :param time_to_leave_seconds: TTL for the cache
        :param config_store_class: Customizable ConfigStore caching provider
        """
        self._config_fetcher = CacheControlConfigFetcher(project_secret)
        if config_store_class:
            self._config_store = config_store_class(self._config_fetcher)
        else:
            self._config_store = InMemoryConfigStore(self._config_fetcher, time_to_leave_seconds)

    def get_configuration_json(self):
        """
        Gets the configuration as a json string.
        :return: the configuration as a json string. Returns None if the configuration fetch from the network fails.
        """
        return self._config_store.get()

    def get_value(self, key, default_value):
        """  Gets a value from the configuration identified by the given key.
        :param key: the identifier of the configuration value.
        :param default_value: in case of any failure, this value will be returned.
        :return: the configuration value identified by the given key.
        """
        config = self._config_store.get()
        if config is None or key not in config:
            return default_value

        return config[key]

    def invalidate_cache(self):
        """
        Invalidates the internal ConfigStore implementation's cache.
        :return:
        """
        self._config_store.invalidate_cache()

    def close(self):
        """
        Closes all resources
        :return:
        """
        self._config_fetcher.close()
