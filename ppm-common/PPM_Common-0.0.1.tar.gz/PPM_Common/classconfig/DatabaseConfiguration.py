# -*- coding: utf-8 -*-
"""
..  py:module:: DatabaseConfiguration

This module contains DatabaseConfiguration class
"""

from PPM_Common.classconfig.ElasticConfiguration import ElasticConfiguration
from PPM_Common.classconfig.MongoConfiguration import MongoConfiguration

class DatabaseConfiguration(object):
    """
    Class for database configuration

    """

    def __init__(self):
        """
        Constructor
        :rtype: object
        """
        # mongo configuration
        self.__mongoConf = MongoConfiguration()
        # elastic search configuration
        self.__elasticConf = ElasticConfiguration()


    def setMongoConf(self, mongoConf):
        """
        Setter
        :param host: new value
        :type mongoConf: MongoConfiguration
        """
        self.__mongoConf = mongoConf

    def getMongoConf(self):
        """
        Getter
        :return: mongoConf value
        :rtype: MongoConfiguration
        """
        return self.__mongoConf

    def setElasticConf(self, elasticConf):
        """
        Setter
        :param elasticConf: new value
        :type elasticConf: ElasticConfiguration
        """
        self.__elasticConf = elasticConf

    def getElasticConf(self):
        """
        Getter
        :return: elasticConf value
        :rtype: ElasticConfiguration
        """
        return self.__elasticConf

    # properties
    mongoConf = property(getMongoConf, setMongoConf)
    elasticConf = property(getElasticConf, setElasticConf)

