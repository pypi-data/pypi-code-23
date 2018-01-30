import configparser
import json
import logging
import logging.config
import os

from eu.softfire.sdn.utils.static_config import CONFIG_FILE_PATH


def get_logger(name):
    # print("Config File: %s"%CONFIG_FILE_PATH)
    logging.config.fileConfig(CONFIG_FILE_PATH)
    return logging.getLogger("eu.softfire.sdn.manager.%s" % name)


def get_config_parser():
    """
    Get the ConfigParser object containing the system configurations

    :return: ConfigParser object containing the system configurations
    """
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_PATH) and os.path.isfile(CONFIG_FILE_PATH):
        config.read(CONFIG_FILE_PATH)
        return config
    else:
        logging.error("Config file not found, please create %s" % CONFIG_FILE_PATH)
        exit(1)


def get_config(section, key, default=None):
    config = get_config_parser()
    if default is None:
        return config.get(section=section, option=key)
    try:
        return config.get(section=section, option=key)
    except configparser.NoOptionError:
        return default


def get_available_resources():
    with open(get_config('system', 'available-sdn-resources-file'), 'r') as f:
        return json.loads(f.read())
