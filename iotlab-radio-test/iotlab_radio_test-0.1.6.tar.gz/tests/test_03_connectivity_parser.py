import filecmp
import os
import tempfile
import unittest
from difflib import unified_diff
from distutils.dir_util import copy_tree

from iotlab_radio_test.cli import connectivity_main

from iotlab_radio_test.config import get_config_from_yaml


class UnitTest03ConnectivityParser(unittest.TestCase):
    def test_from_data(self):
        input_dir = os.path.join('tests', 'test_data_03_connectivity_parser', 'input')
        expected_parsed_dir = os.path.join('tests', 'test_data_03_connectivity_parser', 'output')
        temp_parsed_dir = tempfile.mkdtemp()

        copy_tree(input_dir, temp_parsed_dir)

        config = get_config_from_yaml()
        config.node_list = [4, 5, 9]
        config.radio.channel_list = [19, 20]

        connectivity_main(config, temp_parsed_dir)

        for file in os.listdir(expected_parsed_dir):
            actual_file = os.path.join(temp_parsed_dir, file)
            self.assertTrue(os.path.exists(actual_file))
            expected = os.path.join(expected_parsed_dir,file)

            comparison = filecmp.cmp(expected, actual_file, False)

            if not comparison:
                print(file)
                for line in unified_diff(open(expected,'r').readlines(),open(actual_file,'r').readlines()):
                    print(line)

            self.assertTrue(comparison)
            pass
