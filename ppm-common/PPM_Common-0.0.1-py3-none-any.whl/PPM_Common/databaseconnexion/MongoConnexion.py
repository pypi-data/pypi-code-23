# -*- coding: utf-8 -*-
"""
.. py:module:: MongoConnexion
    :platform: Linux
    :synopsis: Retrieving a connexion to MongoDB

"""

import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from PPM_Common.databaseconnexion.DatabaseConfigurationLoader import DatabaseConfigurationLoader

logger = logging.getLogger("MongoConnexion")


class MongoConnexion(object):
    """
    .. py:class: DatabaseConnexion()

    This class supplies a connection client to MongoDB. The host corresponds to the address of MongoDB database

    """
    def __init__(self, pathToConfigFile):
        self.pathToConfigFile=pathToConfigFile
        self.databaseConfigurationLoader=DatabaseConfigurationLoader(self.pathToConfigFile)

    def getClient(self):
        databaseConfiguration=self.databaseConfigurationLoader.databaseConfiguration.mongoConf
        host = databaseConfiguration.host
        port = databaseConfiguration.port
        try:
            return MongoClient(host,port)
        except ConnectionFailure as cf:
            logger.error("An error occurred when trying to connect to server".format(host))
            raise
        except Exception as e:
            logger.error("Exception = {0}".format(e))
            raise
