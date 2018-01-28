# -*- coding: utf-8 -*-
"""
.. py:module:: ElasticConnexion
    :platform: Linux
    :synopsis: Retrieving a connexion to ElasticSearch

"""

import logging

from elasticsearch import Elasticsearch
from elasticsearch import ConnectionError

from PPM_Common.databaseconnexion.DatabaseConfigurationLoader import DatabaseConfigurationLoader

logger = logging.getLogger("ElasticConnexion")

class ElasticConnexion(object):
    """
    .. py:class: DatabaseConnexion()

    This class supplies a connection to ElasticSearch server. The host corresponds to the address of server

    """
    def __init__(self, pathToConfigFile):
        self.pathToConfigFile=pathToConfigFile
        self.databaseConfigurationLoader=DatabaseConfigurationLoader(self.pathToConfigFile)

    def getClient(self):
        databaseConfiguration=self.databaseConfigurationLoader.databaseConfiguration.elasticConf
        host = databaseConfiguration.host
        port = databaseConfiguration.port
        try:
            return Elasticsearch([{'host': host,'port':port}])
        except ConnectionError as ce:
            logger.error("An error occurred when trying to connect to server".format(host))
            raise
        except Exception as e:
            logger.error("Exception = {0}".format(e))
            raise
