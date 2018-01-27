# coding: utf-8

# Standard Libraries
import json
import logging
import os
import sys
from pathlib import PosixPath

# Cfgtree modules
from cfgtree.storages import ConfigBaseStorage

log = logging.getLogger(__name__)


class JsonFileConfigStorage(ConfigBaseStorage):
    """
    Settings are stored in a single JSON file

    Example:

    .. code-block:: javascript

        {
            'version': 1,
            'general': {
                'verbose': true ,
                'logfile': 'logfile.log'
            }
        }

    Usage:

    .. code-block:: python

        class MyAppConfig(ConfigBaseModel):

            environ_var_prefix = "MYAPP_"

            storage = JsonFileConfigStorage(
                environ_var="MYAPP_COMMON_CONFIG_FILE",
                long_param="--config",
                short_param="-c",
                default_filename="config.json",
            )

            cmd_line_parser = # ...

            model = {
                # repeat in model so the arguments in described in --help
                "configfile": ConfigFileCfg(long_param="--configfile", summary="Config file"),
                # ...
            }

    """

    json_configstorage_default_filename = None
    """Default filename for the configuration file

    Example::

        myconfig.json
    """

    json_configstorage_environ_var = None
    """Environment variable to set the configuration file name

    Example::

       DOPPLERR_COMMON_CONFIG_FILE="myconfig.json"
    """

    json_configstorage_short_param = None
    """Short parameter to specify the configure file name

    Example::

        -g myconfig.json
    """

    json_configstorage_long_param = None
    """Short parameter to specify the configure file name

    Example::

        --configfile myconfig.json
    """

    __resolved_config_file = None
    __bare_config_dict = None

    def __init__(self, environ_var=None, long_param=None, short_param=None, default_filename=None):
        if environ_var:
            self.json_configstorage_environ_var = environ_var
        if long_param:
            self.json_configstorage_long_param = long_param
        if short_param:
            self.json_configstorage_short_param = short_param
        if default_filename:
            self.json_configstorage_default_filename = default_filename

    def find_storage(self):
        configfile = self.json_configstorage_default_filename
        if self.json_configstorage_environ_var in os.environ:
            configfile = os.environ[self.json_configstorage_environ_var]
            log.debug("%s defined: %s", self.json_configstorage_environ_var, configfile)
        for i in range(len(sys.argv)):
            good = []
            if self.json_configstorage_short_param:
                good.append(self.json_configstorage_short_param)
            if self.json_configstorage_long_param:
                good.append(self.json_configstorage_long_param)
            if sys.argv[i] in good:
                if i == len(sys.argv):
                    raise Exception("No value given to {}".format(" or ".join(good)))
                configfile = sys.argv[i + 1]
                log.debug("%s defined: %s", " or ".join(good), configfile)
                break
        config_file_path = PosixPath(configfile)
        log.debug("Configuration file set to: %s", configfile)
        self.__resolved_config_file = config_file_path.resolve().as_posix()
        self.__load_bare_config()

    def __load_bare_config(self):
        log.debug("Loading configuration file: %s", self.__resolved_config_file)
        config_file_path = PosixPath(self.__resolved_config_file)
        if config_file_path.exists():
            with config_file_path.open() as f:
                self.__bare_config_dict = json.load(f)
        else:
            self.__bare_config_dict = {}

    def save_bare_config_dict(self, bare_cfg):
        with PosixPath(self.__resolved_config_file).open('w') as f:
            f.write(json.dumps(bare_cfg, sort_keys=True, indent=4, separators=(',', ': ')))

    def get_bare_config_dict(self):
        return self.__bare_config_dict
