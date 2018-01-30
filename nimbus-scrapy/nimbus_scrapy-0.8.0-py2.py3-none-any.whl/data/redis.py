# -*- coding: utf-8 -*-
from __future__ import absolute_import
"""
Package Description
"""
import os
import sys
import logging
import json
import redis
from ..decorator import singleton, singleton_

__all__ = ["client", "ClientRedis", ]

DEFAULT_NAME = "default"


@singleton_
class ClientRedis(object):
    connections = {}

    def init(self, name=None, **kwargs):
        if not name:
            return None
        if name in self.connections:
            return self.connections.get(name, None)
        engine = redis.StrictRedis(**kwargs)
        self.connections[name] = engine
        return engine

    def get_connection(self, name=DEFAULT_NAME):
        return self.connections.get(name, None)


client = ClientRedis()
