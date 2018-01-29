# coding: utf-8

# Standard Libraries
import logging
import os
import sys
from pathlib import PosixPath

# Cfgtree modules
from cfgtree.storages import ConfigBaseStorage
from cfgtree.types import ConfigFileCfg

log = logging.getLogger(__name__)


class SingleFileStorage(ConfigBaseStorage):
    default_filename = None

    environ_var = None

    short_param = None

    long_param = None

    __resolved_config_file = None
    __bare_config_dict = None

    def __init__(self, environ_var=None, long_param=None, short_param=None, default_filename=None):
        if environ_var and self.environ_var is None:
            self.environ_var = environ_var
        if long_param and self.long_param is None:
            self.long_param = long_param
        if short_param and self.short_param is None:
            self.short_param = short_param
        if default_filename and self.default_filename is None:
            self.default_filename = default_filename

    def find_default_filename(self, model):
        if self.default_filename:
            return
        for _k, v in model.items():
            if isinstance(v, ConfigFileCfg):
                self.default_filename = v.default_filename
                self.short_param = v.short_param
                self.long_param = v.long_param
                return True
            elif isinstance(v, dict):
                if self.find_default_filename(v):
                    return True

    def find_storage(self, model, argv=None):
        if argv is None:
            argv = sys.argv
        self.find_default_filename(model)
        configfile = self.default_filename
        if self.environ_var and self.environ_var in os.environ:
            configfile = os.environ[self.environ_var]
            log.debug("%s defined: %s", self.environ_var, configfile)
        for i, _ in enumerate(argv):
            good = []
            if self.short_param:
                good.append(self.short_param)
            if self.long_param:
                good.append(self.long_param)
            if argv[i] in good:
                if i == len(argv):
                    raise Exception("No value given to {}".format(" or ".join(good)))
                configfile = argv[i + 1]
                log.debug("%s defined: %s", " or ".join(good), configfile)
                break
        if not configfile:
            raise ValueError("Cannot find which configuration file name to search")
        config_file_path = PosixPath(configfile)
        log.debug("Configuration file set to: %s", configfile)
        self.__resolved_config_file = config_file_path.resolve().as_posix()
        self.__load_bare_config()

    def __load_bare_config(self):
        log.debug("Loading configuration file: %s", self.__resolved_config_file)
        config_file_path = PosixPath(self.__resolved_config_file)
        if config_file_path.exists():
            self.__bare_config_dict = self.load_bare_config(config_file_path)

        else:
            self.__bare_config_dict = {}

    def load_bare_config(self, config_file_path):
        raise NotImplementedError()

    def save_bare_config_dict(self, bare_cfg):
        raise NotImplementedError()

    def get_bare_config_dict(self):
        return self.__bare_config_dict

    def get_config_file(self):
        return self.__resolved_config_file
