import os
import sys
from logging import Logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class CloeePyMongo(object):
    """
    Class representing the CloeePy MongoDB plugin
    """
    def __init__(self, config:dict, log:Logger):
        # make a copy of the config so we're not messing with the original values
        info = config.copy()

        # set pluginNamespace
        self._namespace = None
        if "pluginNamespace" in info:
            self.namespace = info["pluginNamespace"]
            del info["pluginNamespace"]
        else:
            self._namespace = "mongo"

        # use environment variables for username and password if they exist
        if 'CLOEEPY_MONGO_USERNAME' in os.environ and 'CLOEEPY_MONGO_PASSWORD' in os.environ:
            log.info("Pymongo: Using credentials defined in environment")
            info['username'] = os.environ['CLOEEPY_MONGO_USERNAME']
            info['password'] = os.environ['CLOEEPY_MONGO_PASSWORD']

        # connect
        log.info("Dialing MongoDB")
        self.conn = MongoClient(**info)

        # verify connection
        try:
            # The ismaster command is cheap and does not require auth.
            self.conn.admin.command('ismaster')
        except ConnectionFailure:
            msg = "Failed to connect to MongoDB"
            log.error(msg)
            sys.exit(msg)
        else:
            log.info("Established connection to MongoDB")

    def get_namespace(self):
        return self._namespace

    def get_value(self):
        return self.conn
