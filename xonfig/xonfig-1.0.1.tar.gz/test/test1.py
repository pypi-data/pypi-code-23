# -*- coding: utf-8 -*-
"""
Test with no configuration. There is no config file and there is no environment variable.
"""

import unittest
from configparser import ConfigParser, NoSectionError

from xonfig import *


class Test1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_01_config_files_detected(self):
        # No config file loaded
        self.assertEqual(len(get_config_files_detected()), 0)

    def test_02_config_type(self):
        # Test config object is instance of ConfigParser
        self.assertIsInstance(get_config(), ConfigParser)

    def test_03_get_env(self):
        # Detected environment should be None because no __ENV__ declared in environment variables
        self.assertEqual(get_env(), None)

    def test_04_empty_sections(self):
        # _config_file_detected should be None. No config file loaded.
        self.assertEqual(get_config_files_detected(), [])

    def test_05_empty_sections(self):
        # _sections should be {}. There is no section loaded neither file nor environment variables.
        self.assertEqual(get_sections(), {})

    def test_06_no_section(self):
        # KeyError should be raised because there is no section named 'SECT1'.
        with self.assertRaises(KeyError):
            get_section('SECT1')

    def test_07_no_section(self):
        # NoSectionError should be raised because there is no section named 'SECT1'.
        with self.assertRaises(NoSectionError):
            get_option('SECT1', 'OPT1')


if __name__ == '__main__':
    unittest.main()
