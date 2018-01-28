# -*- coding: utf-8 -*-
"""
.. py:module:: DatabaseConfigurationLoader
    :platform: Linux
    :synopsis: Getting data configuration from JSON configuration file for MongoDB datasource and Elasticsearch datasource

Usage :
    from PPM_Common import DatabaseConfigurationLoader
    DatabaseConfigurationLoader(pathToConfigFile)

"""

import json
import logging
import os

from PPM_Common.classconfig.DatabaseConfiguration import DatabaseConfiguration
from PPM_Common.json.JSONConstant import JSONConstant
from PPM_Common.exception.ParseConfigurationException import ParseConfigurationException
from PPM_Common.json.JSONUtils import JSONUtils

logger = logging.getLogger("DatabaseConfigurationLoader")


class DatabaseConfigurationLoader(object):
    """
    ..  py:class:: DatabaseConfigurationLoader()

    This class loads the json configuration file for MongoDB datasource

    .. warning:: Adding new configuration's field into :py:class::`JSONConstant` class

    """

    def __init__(self,pathToConfigFile):
        """
        Constructor
        """
        # path to json config file
        self.__pathToConfigFile = pathToConfigFile

        logger.debug("__init__, __pathToConfigFile = %s", self.__pathToConfigFile)

        # check configFile existence
        if not os.path.isfile(self.__pathToConfigFile):
            logger.error("__init__ : __pathToConfigFile do not exist, __pathToConfigFile=%s", self.__pathToConfigFile)

        self.__databaseConfiguration = self.__loadConfiguration()


    def __loadConfiguration(self):
        """
        load json file and return a DatabaseDataSource object
        :return: databaseConfiguration
        :rtype: DatabaseConfiguration
        :raises: ValueError
        """
        try:
            # try to read the json file
            if not self.__pathToConfigFile:
                raise ValueError("pathToConfigFile is set to None")

            with open(self.__pathToConfigFile, 'r') as f:
                jsonFile=f.read()

            if not jsonFile:
                raise Exception("the json config file is empty")

            # json --> dict
            jsonData = json.loads(jsonFile)

            # load data
            databaseConfiguration = self._loadAndCheck(jsonData)

        except ParseConfigurationException as pce:
            logger.error("An error occurred when trying to load configuration")
            raise
        except Exception as e:
            logger.error("Exception = %s", e)

        f.close()

        return databaseConfiguration

    def _loadAndCheck(self, jsonData):
        """
        Check the validity of the json properties file and load it

        :param jsonData: data from json config
        :type jsonData: dict
        :return: dataBaseConfiguration
        :rtype: DatabaseConfiguration
        :raises: TypeError, ParseConfigurationException
        """
        databaseConfiguration = DatabaseConfiguration()

        if not isinstance(jsonData, dict):
            raise TypeError("jsonData must be a dict type")

        if (jsonData.get(JSONConstant.MONGO)):
            mongoData = jsonData.get(JSONConstant.MONGO)
            if not isinstance(mongoData,dict):
                raise TypeError("jsonData for Mongo configuration must be a dict type")

            if not mongoData.get(JSONConstant.HOST):
                raise ParseConfigurationException("config file for Mongo must have a %s item" % JSONConstant.HOST)

            databaseConfiguration.mongoConf.host = mongoData.get(JSONConstant.HOST)

            if not mongoData.get(JSONConstant.PORT):
                raise ParseConfigurationException("config file for Mongo must have a %s item" % JSONConstant.PORT)

            databaseConfiguration.mongoConf.port = mongoData.get(JSONConstant.PORT)

            if JSONUtils().search_value(JSONConstant.LOGIN, mongoData):
                if not mongoData.get(JSONConstant.LOGIN):
                    raise ParseConfigurationException("config file for Mongo must have a %s item" % JSONConstant.LOGIN)

                databaseConfiguration.mongoConf.login = mongoData.get(JSONConstant.LOGIN)

            if JSONUtils().search_value(JSONConstant.PASSWORD, mongoData):
                if not mongoData.get(JSONConstant.PASSWORD):
                    raise ParseConfigurationException("config file for Mongo must have a %s item" % JSONConstant.PASSWORD)

                databaseConfiguration.mongoConf.password = mongoData.get(JSONConstant.PASSWORD)

            if (jsonData.get(JSONConstant.ELASTIC)):
                elasticData = jsonData.get(JSONConstant.ELASTIC)
                if not isinstance(elasticData, dict):
                    raise TypeError("jsonData for Elastic configuration must be a dict type")

                if not elasticData.get(JSONConstant.HOST):
                    raise ParseConfigurationException("config file for Elastic must have a %s item" % JSONConstant.HOST)

                databaseConfiguration.elasticConf.host = elasticData.get(JSONConstant.HOST)

                if not elasticData.get(JSONConstant.PORT):
                    raise ParseConfigurationException("config file for Elastic must have a %s item" % JSONConstant.PORT)

                databaseConfiguration.elasticConf.port = elasticData.get(JSONConstant.PORT)

                if JSONUtils().search_value(JSONConstant.LOGIN, elasticData):
                    if not elasticData.get(JSONConstant.LOGIN):
                        raise ParseConfigurationException("config file for Elastic must have a %s item" % JSONConstant.LOGIN)

                    databaseConfiguration.elasticConf.login = elasticData.get(JSONConstant.LOGIN)

                if JSONUtils().search_value(JSONConstant.PASSWORD, elasticData):
                    if not elasticData.get(JSONConstant.PASSWORD):
                        raise ParseConfigurationException("config file for Elastic must have a %s item" % JSONConstant.PASSWORD)

                    databaseConfiguration.elasticConf.password = elasticData.get(JSONConstant.PASSWORD)

                if JSONUtils().search_value(JSONConstant.MODE, elasticData):
                    if not elasticData.get(JSONConstant.MODE):
                        raise ParseConfigurationException(
                            "config file for Elastic must have a %s item" % JSONConstant.MODE)

                    databaseConfiguration.elasticConf.mode = elasticData.get(JSONConstant.MODE)

        return databaseConfiguration

    # ----------------------------------------------
    # Getter and Setter
    # ----------------------------------------------

    def setPathToConfigFile(self, pathToConfigFile):
        """
        Setter
        :param pathToConfigFile: path to file
        :type pathToConfigFile: str
        """
        self.__pathToConfigFile = pathToConfigFile

    def getPathToConfigFile(self):
        """
        Getter
        :return: path value
        :rtype: str
        """
        return self.__pathToConfigFile

    def setDatabaseConfiguration(self, databaseConfiguration):
        """
        Setter
        :param databaseConfiguration: new configuration
        :type DatabaseConfiguration
        """
        self.__databaseConfiguration = databaseConfiguration

    def getDatabaseConfiguration(self):
        """
        Getter
        :return: config value
        :rtype: DatabaseConfiguration
        """
        return self.__databaseConfiguration

    # properties

    pathToConfigFile = property(getPathToConfigFile, setPathToConfigFile)
    databaseConfiguration = property(getDatabaseConfiguration, setDatabaseConfiguration)
