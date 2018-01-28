# -*- coding: utf-8 -*-
"""
..  py:module:: DatabaseDataSource

This module contains DatabaseDataSource class
"""


class MongoConfiguration(object):
    """
    Class for Mongo DB data source data source

    """

    def __init__(self):
        """
        Constructor
        :rtype: object
        """
        # IP address for database
        self._host = None
        # Port for database
        self.__port = None
        # login for database
        self.__login = None
        # password for database
        self.__password = None

    def setHost(self, host):
        """
        Setter
        :param host: new value
        :type host: str
        """
        self._host = host

    def getHost(self):
        """
        Getter
        :return: host value
        :rtype: str
        """
        return self._host

    def setPort(self, port):
        """
        Setter
        :param port: new value
        :type port: int
        """
        self.__port = port

    def getPort(self):
        """
        Getter
        :return: port value
        :rtype: int
        """
        return self.__port

    def setLogin(self, login):
        """
        Setter
        :param login: new value
        :type login: str
        """
        self.__login = login

    def getLogin(self):
        """
        Getter
        :return: login value
        :rtype: str
        """
        return self.__login

    def setPassword(self, password):
        """
        Setter
        :param password: new value
        :type password: str
        """
        self.__password = password

    def getPassword(self):
        """
        Getter
        :return: password
        :rtype: str
        """
        return self.__password

    # properties
    host = property(getHost, setHost)
    port = property(getPort, setPort)
    login = property(getLogin, setLogin)
    password = property(getPassword, setPassword)
