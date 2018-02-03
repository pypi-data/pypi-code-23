# -*- coding: utf-8 -*-

"""
Test with config.ini and config.development.ini files. Simulating development environment.
"""

import os
import unittest

from xonfig import get_option, get_section, get_config_files_detected

this_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class Test2(unittest.TestCase):
    def test_01_config_files_detected(self):
        # There should be 2 configuration file loaded. config.ini and config.development.ini
        self.assertEqual(len(get_config_files_detected()), 2)
        self.assertEqual(get_config_files_detected()[0].endswith('config.ini'), True)
        self.assertEqual(get_config_files_detected()[1].endswith('config.development.ini'), True)

    def test_02_get_section(self):
        # APP section  from config.ini
        self.assertIsInstance(get_section('APP'), dict)

        # X_API section from config.development.ini
        self.assertIsInstance(get_section('X_API'), dict)

        # FOO section from config.development.ini
        self.assertIsInstance(get_section('FOO'), dict)

    def test_03_get_option(self):
        # First declared in config.ini overwritten by config.development.ini
        self.assertEqual(get_option('APP', 'DEVELOPMENT'), True)
        self.assertEqual(get_option('APP', 'DEBUG'), True)

        # Only declared in config.ini
        self.assertEqual(get_option('APP', 'SQLALCHEMY_TRACK_MODIFICATIONS'), False)

        # Only declared in config.development.ini
        self.assertEqual(get_option('X_API', 'KEY'), 'fweffqdqfedefwefewf')


if __name__ == '__main__':
    unittest.main()
