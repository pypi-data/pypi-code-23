import copy
import logging
import os
import threading
from inspect import signature
import random
import datetime

import etcd
from consul_kv import Connection


class KVStore:
    _logger = logging.getLogger('KVStore')

    _etcd_client = None
    _consul_kv = None
    _kv_prefix = None

    _reload_enabled = False

    # Initializes the KVStore
    def __init__(self,
                 consul_host=None,
                 consul_port=None,
                 etcd_host=None,
                 etcd_port=None,
                 kv_prefix=None,
                 reload_seconds=None,
                 reload_enabled=None,
                 initial_config={}):

        self._config = initial_config
        self._old_config = {}
        self._reload_seconds = 20
        self._on_reload_listeners = []

        # Set Defaults and Get From Environment
        consul_host = consul_host or os.getenv("CONSUL_HOST")
        consul_port = int(consul_port or os.getenv("CONSUL_PORT", 8500))
        etcd_host = etcd_host or os.getenv("ETCD_HOST", "localhost")
        etcd_port = int(etcd_port or os.getenv("ETCD_PORT", 2379))
        kv_prefix = kv_prefix or os.getenv("KV_PREFIX", "")
        reload_seconds = int(reload_seconds or os.getenv("RELOAD_CONFIG_PERIOD", 20))
        reload_enabled = bool(reload_enabled or os.getenv("RELOAD_ENABLED", False))

        self._logger.info("Initializing KVStore...")

        self._reload_seconds = reload_seconds
        self._reload_enabled = reload_enabled

        self._kv_prefix = kv_prefix
        if consul_host:
            url = "http://{0}:{1}/v1/".format(consul_host, consul_port)
            self._logger.info("Making connection to Consul at {0}".format(url))
            self._consul_kv = Connection(endpoint=url)
            if kv_prefix and len(kv_prefix) > 0 and kv_prefix[0] == "/":
                self._kv_prefix = kv_prefix[1:]

        elif etcd_host:
            self._logger.info("Making connection to ETCD at {0}:{1}".format(etcd_host, etcd_port))
            self._etcd_client = etcd.Client(host=etcd_host, port=etcd_port)

        self._logger.info("KV Prefix {0}".format(self._kv_prefix))

        if reload_enabled:
            self._reload_configuration()
        else:
            self._read_config()

    # Add an on_reload callback
    def on_reload(self, on_reload_callback):
        self._logger.debug("on_reload_callback: {0}".format(str(on_reload_callback)))
        self._on_reload_listeners.append(on_reload_callback)

    # Set the on_reload callback
    def remove_on_reload(self, on_reload_callback):
        self._logger.debug("on_reload_callback: {0}".format(str(on_reload_callback)))
        self._on_reload_listeners.remove(on_reload_callback)

    # Enables Reloading
    def enable_reloading(self, reload_seconds=20):
        self._reload_seconds = reload_seconds
        self._reload_enabled = True
        self._reload_configuration()

    # Disables Reloading
    def disable_reloading(self):
        self._reload_enabled = False

    # Read Configuration from Consul or ETCD.
    def _read_config(self):
        self._logger.debug("Reloading configuration...")
        self._old_config = self._config

        # Read from consul if present
        if self._consul_kv:
            self._config = self._consul_kv.get_dict(self._kv_prefix)
            keys = self._kv_prefix.split("/")
            for key in keys:
                temp_config = self._config.get(key)
                if temp_config:
                    self._config = temp_config

        # Read from etcd if present
        elif self._etcd_client:
            self._config = self._extract_etcd_config(self._kv_prefix)

        self._logger.debug("Configuration reloaded.")

        # Make sure there is at least a non empty config.
        if not self._old_config:
            self._old_config = {}

        if not self._config:
            self._config = {}

        self._notify_on_reload_listeners()

    def _notify_on_reload_listeners(self):
        # Notify the on-reload listeners.
        for listener in self._on_reload_listeners:
            if listener and callable(listener):
                if len(signature(listener).parameters) == 2:
                    self._logger.debug("Notifying on_reload callback method: {0}".format(str(listener)))
                    threading.Thread(target=listener(self._old_config, self._config),
                                     name="KVStoreNotifyThread-{0}-{1}"
                                     .format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                     self._random_string())).start()
                else:
                    self._logger.error("Expected 2 parameters on on_reload function.")
            else:
                self._logger.error("Listener is not a callable function.")



    def _random_string(self):
        return str(random.randrange(0, 999999)).zfill(6)

    # Watch the configuration
    def _reload_configuration(self):
        # Starts a thread to reload the configuration periodically, this needs to happen before reloading the config,
        # in case the notify function blocks.
        if self._reload_enabled:
            self._logger.debug("Reloading configuration every {0} seconds.".format(self._reload_seconds))
            threading.Timer(self._reload_seconds, self._reload_configuration).start()

        # Load the config and notify the listeners.
        self._read_config()


    # Gets all attributes for an etcd config given a root node.
    def _extract_etcd_config(self, etcd_path):
        local_config = {}
        etcd_config = self._etcd_client.read(etcd_path, recursive=True, sorted=True)
        for child in etcd_config.children:
            self._set_attribute(local_config, child.key[len(etcd_path) + 1:], child.value)
        return local_config

    # Sets a deep attribute on a dict given an attribute delimited with a /
    def _set_attribute(self, a_dict, key, value):
        last_dict = a_dict
        i = 0
        keys = key.split("/")
        for iter_key in keys:
            i = i + 1
            if i == len(keys):
                last_dict[iter_key] = value
            else:
                prev_last_dict = last_dict
                last_dict = last_dict.get(iter_key)
                if not last_dict:
                    last_dict = {}
                    prev_last_dict[iter_key] = last_dict

    # Returns true if the config attribute is different between the old and new value.
    def attribute_changed(self, *keys):

        for key in keys:
            if str(self._config.get(key)) != str(self._old_config.get(key)):
                self._logger.debug("Key {0} changed.".format(key))
                return True
        self._logger.debug("Values of {0} did NOT change.".format(str(keys)))
        return False

    def get(self, key, default=None):
        value = None
        if key:
            keys = key.split("/")
            value = self._config
            for k in keys:
                if value and type(value) is dict:
                    value = value.get(k)
                else:
                    value = None
                    break

        return copy.deepcopy(value or default)

    def get_dict(self, default=None):
        return copy.deepcopy(self._config) or default

    def get_old_dict(self, default=None):
        return copy.deepcopy(self._old_config) or default
