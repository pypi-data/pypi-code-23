# -*- coding: utf-8 -*-

"""
Test with only config.ini file.
"""

import os
import unittest
from configparser import NoOptionError

from xonfig import get_option, get_section, get_sections, get_config_files_detected

this_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class Test2(unittest.TestCase):
    def test_01_config_files_detected(self):
        # Check if only one config file(config.ini) loaded
        self.assertEqual(len(get_config_files_detected()), 1)
        self.assertEqual(get_config_files_detected()[0].endswith('config.ini'), True)

    def test_02_get_section(self):
        # Test APP section exists in config
        self.assertIsInstance(get_section('APP'), dict)

    def test_03_get_sections(self):
        # Test APP section exists in config
        self.assertIsInstance(get_sections()['APP'], dict)

    def test_04_get_section(self):
        # KeyError should be raised because there is no section named 'DB' in config
        with self.assertRaises(KeyError):
            get_section('DB')

    def test_05_get_option(self):
        # Get option tests
        self.assertEqual(get_option('APP', 'DEBUG'), True)
        self.assertEqual(get_option('APP', 'SECRET_KEY'), 'VERY-SECRET-K3Y')
        self.assertEqual(get_option('APP', 'SQLALCHEMY_POOL_SIZE'), 100)
        self.assertEqual(get_option('APP', 'X_RATE'), 1.23)

    def test_06_get_option_by_dict(self):
        # Get option directly from dictionary
        self.assertEqual(get_section('APP')['DEVELOPMENT'], True)
        self.assertEqual(get_section('APP')['SECRET_KEY'], 'VERY-SECRET-K3Y')

    def test_07_get_option(self):
        # Should be raise NoOptionError
        with self.assertRaises(NoOptionError):
            self.assertEqual(get_option('APP', 'DEBUG1'), True)


if __name__ == '__main__':
    unittest.main()
