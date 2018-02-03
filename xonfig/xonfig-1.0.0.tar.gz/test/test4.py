# -*- coding: utf-8 -*-
"""
Test with config.ini, config.production.ini files and environment variables. Simulating production environment.
"""

import os
import unittest

from xonfig import (
    get_option,
    get_section,
    get_config_files_detected,
    set_config_dir,
    get_env,
    get_config_dir
)

this_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class Test2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_dir = os.path.join(this_dir, 'temp')
        cls.config_dir = config_dir

        set_config_dir(config_dir)

    def test_01_get_config_dir(self):
        # Test config dir properly configured
        self.assertEqual(get_config_dir(), self.config_dir)

    def test_02_get_env(self):
        # Environment should be production
        self.assertEqual(get_env(), 'production')

    def test_03_config_files_detected(self):
        # There should be 2 configuration file loaded. config.ini and config.development.ini
        self.assertEqual(len(get_config_files_detected()), 2)
        self.assertEqual(get_config_files_detected()[0].endswith('config.ini'), True)
        self.assertEqual(get_config_files_detected()[1].endswith('config.production.ini'), True)

    def test_04_get_section(self):
        # APP section  from config.ini
        self.assertIsInstance(get_section('APP'), dict)

        # FOO section from environment variables
        self.assertIsInstance(get_section('FOO'), dict)

    def test_05_get_option(self):
        # First declared in config.ini overwritten by config.production.ini
        self.assertEqual(get_option('APP', 'X_RATE'), 1.80)

        # First declared in config.ini overwritten by config.production.ini and then overwritten by environment vars
        self.assertEqual(get_option('APP', 'BASE_URL'), 'http://0.0.0.0:5004')

        # Declared in environment vars
        self.assertEqual(get_option('APP', 'SQLALCHEMY_DATABASE_URI'), 'postgresql://talhasch:@localhost:5434/db_name')

        # Declared in config.ini
        self.assertEqual(get_option('APP', 'SQLALCHEMY_TRACK_MODIFICATIONS'), False)

        # Declared in environment vars
        self.assertEqual(get_option('APP', 'SQLALCHEMY_POOL_SIZE'), 100)


if __name__ == '__main__':
    unittest.main()
