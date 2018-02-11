# coding=utf-8
"""
Manages Config
"""
# pylint: disable=too-few-public-methods

import os

import everett
import everett.manager

from .yaml_config import YAMLConfig


class BaseConfig:
    """
    Singleton configuration class for EDLM.
    """

    def __init__(self, package_name: str, default_dict: dict = None):

        if default_dict is None:
            default_dict = {}
        self._config = everett.manager.ConfigManager(
            [
                everett.manager.ConfigEnvFileEnv('.env'),
                everett.manager.ConfigOSEnv(),
                YAMLConfig(
                    [
                        os.environ.get(f'{package_name.upper()}_YAML'),
                        os.path.join(os.path.expanduser(
                            '~'), f'{package_name}.yml'),
                        os.path.join(os.path.expanduser('~'),
                                     f'{package_name}.yaml'),
                        f'./{package_name}.yml',
                        f'./{package_name}.yaml',
                    ]
                ),
                everett.manager.ConfigIniEnv(
                    [
                        os.environ.get(f'{package_name.upper()}_INI'),
                        os.path.join(os.path.expanduser(
                            '~'), f'{package_name}.ini'),
                        f'./{package_name}.ini',
                    ]
                ),
                everett.manager.ConfigDictEnv(default_dict),
            ]
        )
