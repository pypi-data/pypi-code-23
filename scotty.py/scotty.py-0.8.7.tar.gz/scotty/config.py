import os
import logging

import ConfigParser
import appdirs

from scotty.core.exceptions import ScottyException


class ScottyConfig(object):
    _raw_config = {'logging': {'log_format': True}}
    _config_suffixes = ['.conf']

    def __init__(self):
        self._appdirs = appdirs.AppDirs('scotty', multipath='/etc')
        self._base_dir = {}
        self._path = self._find_config_file()
        self._load()

    @property
    def _config_files(self):
        config_files = []
        for path in self._config_search_paths:
            for suffix in self._config_suffixes:
                config_file = os.path.join(path, 'scotty{}'.format(suffix))
                config_files.append(config_file)
        return config_files

    @property
    def _config_search_paths(self):
        search_paths = []
        search_paths.append(self._app_config)
        search_paths.append(self._unix_home_config)
        search_paths.append(self._home_etc)
        search_paths.append(self._unix_home_etc)
        search_paths.append(self._site_etc)
        search_paths.append(self._unix_site_etc)
        return search_paths
   
    @property
    def _app_config(self):
        here = os.path.abspath(os.path.dirname(__file__))
        here = os.path.join(here, '../') 
        here = os.path.normpath(here)
        return os.path.join(here, 'etc')

    @property
    def _unix_home_config(self):
        return os.path.join(os.path.expanduser(os.path.join('~', '.config')), 'scotty')

    @property
    def _home_etc(self):
        return os.path.join(os.path.expanduser(os.path.join('~', '.local/etc')), 'scotty') 

    @property
    def _unix_home_etc(self):
        return '/usr/local/etc/scotty'

    @property
    def _site_etc(self):
        return self._appdirs.site_config_dir

    @property
    def _unix_site_etc(self):
        return '/etc/scotty'

    def _find_config_file(self):
        for path in self._config_files:
            if os.path.exists(path):
                return path
        return None

    @property
    def base_dir(self):
        if not self._base_dir:
            self._base_dir = os.path.dirname(self._path)
        return self._base_dir

    def _load(self):
        self._config = ConfigParser.ConfigParser()
        self._config.read(self._path)

    def _abspath(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.base_dir, path)
            path = os.path.normpath(path)
        return path

    def _is_raw(self, section, option):
        if section in self._raw_config:
            return self._raw_config[section].get(option, False)

    def get(self, section, option, abspath=False):
        value = self._config.get(section, option, self._is_raw(
            section, option))
        if abspath:
            value = self._abspath(value)
        return value
