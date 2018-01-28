#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2018 TUNE, Inc. (http://www.tune.com)
#  @namespace pymemcache-client

import os
import ujson as json
import telnetlib
import re
import socket
from pymemcache.client.hash import HashClient
from pymemcache.client.base import Client as BasicClient
# from pprintpp import pprint

class PymemcacheClient(object):

    _memcached_servers = []
    _client_type = None
    _server_type = None
    _cache_client = None

    _config = {
        "client_type": "basic",
        "servers": [
            {
                "host": "localhost",
                "port": 11211
            }
        ],
        "server_type": "standard",
        "connect_timeout": None,
        "timeout": None,
        "no_delay": False,
        "ignore_exc": False,
        "default_noreply": True,
        "allow_unicode_keys": False,
    }

    @property
    def memcached_servers(self):
        return self._memcached_servers

    @property
    def client_type(self):
        return self._client_type
    @client_type.setter
    def client_type(self, value):
        self._client_type = value

    @property
    def server_type(self):
        return self._server_type
    @server_type.setter
    def server_type(self, value):
        self._server_type = value

    @property
    def config(self):
        return self._config
    @config.setter
    def config(self, value):
        self._config = value

    @property
    def cache_client(self):
        return self._cache_client
    @cache_client.setter
    def cache_client(self, value):
        self._cache_client = value

    def __init__(self, config=None, config_file=None, **kwargs):
        """Prepare a Pymemcache client using available configuration.

        Keyword arguments:
        config
        config_file
        kwargs
        """

        if config is None:
            config = self.config

        try:
            config = configFromFile(config, os.path.expanduser("~/.pymemcache.json"))
        except:
            pass

        config = configFromEnv(config)
        config = configFromFile(config, "pymemcache.json")
        config = configFromFile(config, config_file)
        config = configFromArgs(config, **kwargs)

        required_fields = ["servers"]

        optional_fields = [
            "client_type",
            "server_type",
            "connect_timeout",
            "timeout",
            "no_delay",
            "ignore_exc",
            "default_noreply",
            "allow_unicode_keys"
        ]

        for field in required_fields:
            if field not in config or config[field] is None:
                raise ValueError("No %s set. %s is a required field." % (field, field))

        for field in optional_fields:
            if field not in config:
                config[field] = self.config[field]

        if "client_type" in config:
            if config["client_type"] not in ["basic", "hash"]:
                raise ValueError("Value in %s is not valid: '%s'." % ("client_type", config["client_type"]))

            self.client_type = config["client_type"]
        else:
            self.client_type = "basic"

        if "server_type" in config:
            if config["server_type"] not in ["standard", "elasticache"]:
                raise ValueError("Value in %s is not valid: '%s'." % ("server_type", config["server_type"]))

            self.server_type = config["server_type"]
        else:
            self.server_type = "standard"

        if "servers" in config and (type(config["servers"]) is not list or len(config["servers"]) == 0):
            raise ValueError("No %s set. %s must of be a list of 1 or more values." % ("servers", "servers"))

        if self.client_type == "basic" and len(config["servers"]) > 1:
            raise ValueError("Client type '%s' cannot have more than 1 server: %d" % (self.client_type, len(config["servers"])))

        for k, v in config.items():
            setattr(self, k, v)

        self._memcached_servers = []
        required_server_fields = ["host", "port"]
        for server in config["servers"]:
            for field in required_server_fields:
                if field not in server or server[field] is None:
                    raise ValueError("No %s set in server. %s is a required field." % (field, field))

            host = socket.gethostbyname("localhost") if server["host"] == "localhost" else server["host"]

            if "server_type" in config and config["server_type"] == "elasticache":
                self._memcached_servers.append(self.aws_elasticache_endpoints(host, server["port"]))
            else:
                self._memcached_servers.append((host, server["port"]))

        self.cache_error = None

        if type(self.memcached_servers) is not list or len(self.memcached_servers) == 0:
            raise ValueError("Memcache type '%s' has not been assigned any servers." % (self.client_type))

        if self.client_type == "hash":
            self.cache_client = HashClient(
                servers=self.memcached_servers,
                connect_timeout=config["connect_timeout"],
                timeout=config["timeout"],
                no_delay=config["no_delay"],
                ignore_exc=config["ignore_exc"],
                allow_unicode_keys=config["allow_unicode_keys"]
            )
        elif self.client_type == "basic":
            if len(self.memcached_servers) != 1:
                raise ValueError("Memcache type '%s' must be assigned only 1 server." % (self.client_type))

            self.cache_client = BasicClient(
                server=self.memcached_servers[0],
                connect_timeout=config["connect_timeout"],
                timeout=config["timeout"],
                no_delay=config["no_delay"],
                allow_unicode_keys=config["allow_unicode_keys"]
            )
        else:
            raise ValueError("Unexpected memcache type: '%s'." % (self.client_type))

        if self.cache_client is None:
            raise ValueError("Memcache client not created for type '%s'." % (self.client_type))

    def aws_elasticache_endpoints(self, host, port):
        # We're using elasticache cache engine >= 1.4.14 "config get" must be used
        # http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/AutoDiscovery.AddingToYourClientLibrary.html

        command = "config get cluster\n".encode('ascii')
        tn = telnetlib.Telnet(host, port)
        tn.write(command)
        ret = tn.read_until(b"END").decode("utf-8")
        tn.close()

        p = re.compile(r'\r?\n')
        conf = p.split(ret)

        servers = []

        if len(conf) != 5 or conf[4] != 'END':
            raise ValueError("Invalid discovery response")

        nodes_str = conf[2].split(' ')
        for node_str in nodes_str:
            node_list = node_str.split('|')  # host|ip|port
            if len(node_list) != 3:
                raise ValueError("Invalid cluster configuration")
            servers.append((node_list[1], int(node_list[2])))

        return servers


def configFromFile(config, path):
    if path is None:
        return config
    if not os.path.exists(path):
        return config
    try:
        file = open(path, "r")
    except IOError:
        return config

    raw = json.loads(file.read())
    file.close()

    for k in raw.keys():
        if k in config:
            config[k] = raw[k]

    return config


def configFromEnv(config):
    ENV_PREFIX = "PYMEMCACHE"
    for k in config.keys():
        key = "%s_%s" % (ENV_PREFIX, k)
        if key.upper() in os.environ:
            config[k] = os.environ[key.upper()]
    return config


def configFromArgs(config, **kwargs):
    for k in kwargs:
        if kwargs[k] is not None:
            config[k] = kwargs[k]
    return config


def intersect(a, b):
    return list(set(a) & set(b))
