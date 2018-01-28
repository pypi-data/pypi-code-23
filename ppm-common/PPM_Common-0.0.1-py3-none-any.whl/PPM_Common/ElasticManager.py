# -*- coding: utf-8 -*- #
"""
.. py:module:: MongoManager
    :platform: Linux
    :synopsis: A database manager to supply an instance of Elasticsearch

"""

from PPM_Common.databaseconnexion.ElasticConnexion import ElasticConnexion

import logging

logger = logging.getLogger("ElasticManager")

__all__=['ElasticManager']

class ElasticManager(object):
    """
    .. py:class: ElasticManager()

    This class retrieves the connection client of an Elasticsearch instance.
    """

    def __init__(self, pathToConfigFile):
        self.client = ElasticConnexion(pathToConfigFile).getClient()

    def get_client(self):
        return self.client

