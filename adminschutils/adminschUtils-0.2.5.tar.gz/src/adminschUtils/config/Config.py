"""
Configuration wrapper class.
"""
import os
import sys
import copy
import yaml
import logging

from frozendict import frozendict
from voluptuous.error import MultipleInvalid

from .schema import serviceSchema


class Config(object):
    """Configuration class
    Known issues / limitations:
    - frozendict module only froze the keys thus the values can be modified from anywhere.

    Singletone class for config management.
    """
    __instance = None
    _logging_conf = None
    _service_conf = None
    _service_config_file_name = 'service.yaml'
    _logging_config_file_name = 'logging.yaml'

    current_dir = os.path.dirname(__file__)
    _root_dirs = ['/etc/adminsch/',                                      # /etc
                  os.path.join(os.path.dirname(sys.argv[0]), 'config'),  # ./config, . == where the code is running from
                  os.path.join(current_dir, 'config'),  # ./config, . == where this file is located
                  os.path.join(os.getcwd(), 'config')]  # where the cmd was executed
    logger = logging.getLogger(__name__)

    def __new__(cls, config_dir: str = None, *args, **kwargs):  # pylint: disable=unused-argument
        r"""
        Config management class
        Args:
            *args:
            **kwargs:

        Returns:

        """
        if Config.__instance is None:
            Config.__instance = object.__new__(cls)
            if config_dir:
                Config._root_dirs.insert(0, config_dir)

            Config.logger.info("Config manager is initialized")

        return Config.__instance

    def set_logging_conf(self):
        """Setup logging configuration
        Loads the logging config based on the given class parameters.

        Returns:

        """
        Config._logging_conf = frozendict(self.read_config(Config._logging_config_file_name))

    def get_logging_conf(self) -> dict:
        """Get logging conf

        Returns:
            Returns a dictionary with the current config.
        """
        if Config._logging_conf is None:
            self.set_logging_conf()
        return Config._logging_conf

    def set_service_conf(self):
        """Setup logging configuration
        Loads the service config based on the given class parameters.

            Returns:

        """
        Config._service_conf = frozendict(self.read_config(Config._service_config_file_name)['service'])
        self.validate()

    def _read_from_file(self, file_name: str):
        """
        Read and merge default es user provided configs
        Args:
            file_name(str): name of the file

        Returns:
            Return the merged config
        """
        confdir = None

        if os.environ.get('ADMINSCH_CONFDIR', None) is not None:
            Config._root_dirs.insert(0, os.environ['ADMINSCH_CONFDIR'])

        for dir_ in Config._root_dirs:
            if os.path.exists(dir_):
                confdir = dir_
                break

        if confdir is None:
            Config.logger.fatal("Config file is not found.")
            exit(255)

        with open(os.path.join(confdir, file_name)) as conf:
            config = yaml.safe_load(conf.read())

        return config

    def _read_from_envvar(self):
        pass

    def _read_from_sysarg(self):
        pass

    def read_config(self, file_name: str):
        config = self._read_from_file(file_name)
        # config = recursive_dictionary_update.update(config, self._read_from_envvar())
        # config = recursive_dictionary_update.update(config, self._read_from_sysarg())
        return config

    def get_service_conf(self) -> dict:
        """Get service conf

        Returns:
            Returns a dictionary with the current config.
        """
        if Config._service_conf is None:
            self.set_service_conf()
        return Config._service_conf

    def refresh(self):
        """
        Reread all of the config files.
        Returns:

        """
        self.set_logging_conf()
        self.set_service_conf()
        Config.logger.info("Config is refreshed")

    def validate(self):
        try:
            serviceSchema(dict(self.service))
        except MultipleInvalid as exc:
            Config.logger.fatal("Fatal error in config file validation:")
            Config.logger.fatal(str(exc))
            print(str(exc.msg),str(exc.error_message))
            exit(255)

    @property
    def connections_as_list(self) -> list:
        config = []
        for connection_type, connection in self.get_service_conf()['connections'].items():
            for connection_name, conn_conf in connection.items():
                conf = copy.deepcopy(conn_conf)
                conf['name'] = connection_name
                conf['type'] = connection_type
                config.append(conf)
        return config

    @property
    def config(self):
        config = {'service': self.get_service_conf(), 'logging': self.get_logging_conf()}
        return config

    @property
    def logging(self):
        return self.get_logging_conf()

    @property
    def service(self):
        return self.get_service_conf()
