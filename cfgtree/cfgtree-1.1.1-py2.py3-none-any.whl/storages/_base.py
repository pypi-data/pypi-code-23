# coding: utf-8

# Standard Libraries
import logging

log = logging.getLogger(__name__)


class ConfigBaseStorage(object):
    def find_storage(self, model, argv=None):
        """Find the storage location and load the bare configuration"""
        raise NotImplementedError()

    def get_bare_config_dict(self):
        """Returns the bare configuration tree"""
        raise NotImplementedError()

    def save_bare_config_dict(self, bare_cfg):
        """Return the bare configuration into a dict"""
        raise NotImplementedError()
