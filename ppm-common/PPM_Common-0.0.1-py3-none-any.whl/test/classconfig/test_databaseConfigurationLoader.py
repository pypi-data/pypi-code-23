# -*- coding: utf-8 -*-
"""
..  py:module:: test_databaseConfigurationLoader

This module contain TestDatabaseConfigurationLoader class
"""

import os
import sys

sys.path.insert(0,os.path.abspath(__file__+"/../../../../../.."))

from unittest import TestCase

from PPM_Common.databaseconnexion.DatabaseConfigurationLoader import DatabaseConfigurationLoader
from PPM_Common.classconfig.DatabaseConfiguration import DatabaseConfiguration
from settings import CONFIGURATION_DIR_TEST


class TestDatabaseConfigurationLoader(TestCase):
    def setUp(self):
        """
        Setup
        """
        self.pathToConfigFileTest = CONFIGURATION_DIR_TEST + '/databaseConfiguration_test.json'
        self.configLoader = DatabaseConfigurationLoader(self.pathToConfigFileTest)


    def tearDown(self):
        """
        tearDown
        """
        pass

    def test_getConfigurationPath(self):
        """
        Test getPathToConfigFile method
        """
        pathToConfig = self.configLoader.pathToConfigFile
        self.assertEqual(pathToConfig, self.pathToConfigFileTest)


    def test_getConfiguration(self):
        """
        Test getDatabaseConfiguration method
        """
        databaseConfiguration = self.configLoader.databaseConfiguration
        testIp = "127.0.0.1"
        testPort= 27017
        self.assertIsInstance(databaseConfiguration, DatabaseConfiguration)
        self.assertEqual(databaseConfiguration.mongoConf.host, testIp)
        self.assertEqual(databaseConfiguration.mongoConf.port, testPort)


