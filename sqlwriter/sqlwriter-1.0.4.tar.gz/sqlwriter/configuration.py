# -*- coding: utf-8 -*-
import yaml
from sqlwriter.exceptions import SQLWriterConfigException

SUPPORTED_DATABASES = ('mysql', 'postgres')


def get_config(file_name, section):
    """Gets config from yaml file specififed in environment variables

    Parameters
    ----------
    prog: String
        The progam name in the default config.yaml file

    Returns
    -------
    config[prog] : dicionary
        configuration parameters
    """

    with open(file_name, 'r') as f:
        config = yaml.load(f)

    if section is None:
        return config

    try:
        return config[section]
    except KeyError:
        raise SQLWriterConfigException()
