# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" Agent Module handles communication and instrumentation, this
is the main class.
"""

from __future__ import unicode_literals

import json
import os
import threading

from tcell_agent.tcell_logger import get_module_logger
from tcell_agent.utils.tcell_fs import mkdir_p

cacheFileLock = threading.Lock()


class TCellPolicyCache(object):
    """Manages cache."""

    def __init__(self, app_id, cache_dir='tcell/cache'):
        self.app_id = app_id
        mkdir_p(cache_dir)
        self.cache_filename = cache_dir + '/tcell_app.' + self.app_id
        self.pid = os.getpid()
        self.master_cache = {}

    def get_lock(self):
        return cacheFileLock

    def _read_cache(self):
        cache_json = {}
        try:
            if os.path.isfile(self.cache_filename):
                with open(self.cache_filename) as data_file:
                    json_data = data_file.read()
                    cache_json = json.loads(json_data)
        except Exception as e:
            LOGGER = get_module_logger(__name__)
            LOGGER.debug("Error loading cache file")
            LOGGER.debug(e)
            return self.master_cache
        self.master_cache.update(cache_json)
        return self.master_cache

    def current_cache(self):
        self.get_lock().acquire()
        try:
            self._read_cache()
        finally:
            self.get_lock().release()
        return self.master_cache

    def update_cache(self, policy_name, policy_json):
        try:
            self.get_lock().acquire()
            self.master_cache.update({policy_name: policy_json})
            try:
                with open(self.cache_filename, "w") as data_file:
                    json.dump(self.master_cache, data_file, indent=2)
            finally:
                self.get_lock().release()
        except Exception as e:
            LOGGER = get_module_logger(__name__)
            LOGGER.debug("Error writing cache file")
            LOGGER.debug(e)
        return
