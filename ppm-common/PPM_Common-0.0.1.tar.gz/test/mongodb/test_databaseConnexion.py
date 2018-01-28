# -*- coding: utf-8 -*-
"""
..  py:module:: test_databaseConnexion

This module contain TestDatabaseConnexion class
"""

import sys,os

from pymongo import MongoClient

from PPM_Common.databaseconnexion.MongoConnexion import MongoConnexion

sys.path.insert(0,os.path.abspath(__file__+"/../../../../../.."))

from unittest import TestCase
from settings import CONFIGURATION_DIR_TEST


class TestDatabaseConnexion(TestCase):
    def setUp(self):
        """
        Setup
        """
        self.pathToConfigFile = CONFIGURATION_DIR_TEST + '/databaseConfiguration_test.json'
        self.connexion=MongoConnexion(self.pathToConfigFile)

    def tearDown(self):
        """
        tearDown
        """
        self.connexion.getClient().close()

    def test_getClient(self):
        """
        Test get_client method
        """
        self.assertTrue(self.connexion.getClient(),MongoClient)
