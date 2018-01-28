# -*- coding: utf-8 -*-
"""
..  py:module:: test_databaseConfigurationLoader

This module contain TestDatabaseConfigurationLoader class
"""

from unittest import TestCase

from pymongo import MongoClient

from PPM_Common.MongoManager import MongoManager
from settings import CONFIGURATION_DIR_TEST

class TestMongoManager(TestCase):
    def setUp(self):
        """
        Setup
        """
        self.dbName = "TableTest"
        self.pathToConfigFile = CONFIGURATION_DIR_TEST + '/databaseConfiguration_test.json'
        self.databaseManager = MongoManager(self.pathToConfigFile,self.dbName)

    def tearDown(self):
        """
        tearDown
        """
        self.databaseManager.close_db()

    def test_getClient(self):
        """
        Test get_client method
        """
        client = self.databaseManager.get_client()
        self.assertIsNotNone(client)
        self.assertIsInstance(client, MongoClient)

    def test_getDB(self):
        """
        Test get_db method
        """
        db = self.databaseManager.get_db()
        self.assertIsNotNone(db)
        self.assertEqual(db.name,self.dbName)

    def test_getCollection(self):
        """
        Test get_collection method
        """
        pass

    def test_closeDB(self):
        """
        Test the close_db method
        """
        self.assertTrue(self.databaseManager.close_db())

