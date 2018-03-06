from abc import ABCMeta, abstractmethod


class ConfigFetcher(object):
    """
        Config fetcher interface
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, project_secret):
        """
        Initializes the ConfigFetcher
        :param project_secret: The project's Project Secret
        """

    @abstractmethod
    def get_configuration_json(self):
        """
        :return: Returns the configuration json Dictionary
        """

    @abstractmethod
    def close(self):
        """
            Closes the ConfigFetcher's resources
        """


class ConfigStore(object):
    """
        Cache interface
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, config_fetcher):
        """
        Initializes the store with a config_fetcher
        :param config_fetcher: The ConfigFetcher implementation for fetching the configuration from BetterConfig
        """

    @abstractmethod
    def get(self):
        """
        Gets the config json object
        """

    @abstractmethod
    def invalidate_cache(self):
        """
        Invalidates the config cache
        """


class BetterConfigClientException(Exception):
    """
    Generic BetterConfigClientException
    """
