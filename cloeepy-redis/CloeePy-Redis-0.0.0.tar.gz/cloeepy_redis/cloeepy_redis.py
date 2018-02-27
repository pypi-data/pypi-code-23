import os
import sys
from redis import StrictRedis
from logging import Logger

class CloeePyRedis(object):
    def __init__(self, config:dict, log:Logger):
        # make copy of redis configuration and add auto-decoding configuration
        params = config.copy()
        params['encoding'] = 'utf-8'
        params['decode_responses'] = True

        # set pluginNamespace
        self._namespace = "redis"
        if "pluginNamespace" in params:
            self._namespace = params["pluginNamespace"]
            del params["pluginNamespace"]

        # use environment variables for username and password if they exist
        if  "CLOEEPY_REDIS_PASSWORD" in os.environ:
            log.info("CloeePy-Redis: Using password defined in environment")
            params['password'] = os.environ['CLOEEPY_REDIS_PASSWORD']

        log.info("CloeePy-Redis: Dialing Redis")
        self.conn = StrictRedis(**params)

        pong = self.conn.ping()
        if pong == True:
            log.info("CloeePy-Redis: Established connection to Redis")
        else:
            msg = "CloeePy-Redis: Failed to establish connection to Redis"
            log.error(msg)
            sys.exit(msg)


    def get_namespace(self):
        return self._namespace

    def get_value(self):
        return self.conn
