# -*- coding: utf-8 -*- #
"""
.. py:module:: MongoManager
    :platform: Linux
    :synopsis: A database manager to supply an instance of a MongoDB database and a collection among the database

"""

from PPM_Common.databaseconnexion.MongoConnexion import MongoConnexion

import logging

logger = logging.getLogger("MongoManager")

__all__=['MongoManager']

class MongoManager(object):
    """
    .. py:class: DatabaseManager()

    This class creates or retrieves a collection among a specified database. If the database doesn't exist, it is created.
    """

    def __init__(self, pathToConfigFile, dbname):
        self.client = MongoConnexion(pathToConfigFile).getClient()
        self.db = self.client[dbname]

    def get_collection(self, collection_name):
        return self.db.collection_name

    def get_db(self):
        return self.db

    def get_client(self):
        return self.client

    def close_db(self):
        """
        Close connection to mongoDB database
        :param mongo_client: the connection to close
        :type mongo_client: pymongo.MongoClient
        :return: True if success
        """
        try:
            self.client.close()
            return True
        except Exception as e:
            logger.error("Exception = {0}".format(e))
            raise




