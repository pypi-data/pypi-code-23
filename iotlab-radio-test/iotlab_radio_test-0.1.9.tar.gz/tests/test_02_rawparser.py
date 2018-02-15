import filecmp
import unittest
import os
import tempfile
from difflib import unified_diff

from iotlab_radio_test.cli import raw_parser_main
from iotlab_radio_test.config import get_config_from_yaml
from iotlab_radio_test.raw_log_parser import RowLogFileParser


class UnitTest02RawParser(unittest.TestCase):
    def test_from_data(self):
        raw_dir = os.path.join('tests', 'test_data_02_rawparser', 'raw')
        expected_parsed_dir = os.path.join('tests', 'test_data_02_rawparser', 'parsed')
        parsed_dir = tempfile.mkdtemp()

        config = get_config_from_yaml()
        config.radio.channel_list = [11, 12]
        config.radio.txpower_list = [3]
        config.node_list = [1, 5, 9, 29, 33, 37, 53, 57, 61]

        raw_parser_main(config, raw_dir, parsed_dir)

        for file in os.listdir(expected_parsed_dir):
            actual_file = os.path.join(parsed_dir, file)
            self.assertTrue(os.path.exists(actual_file))
            expected = os.path.join(expected_parsed_dir, file)

            comparison = filecmp.cmp(expected, actual_file, False)

            if not comparison:
                print(file)
                for line in unified_diff(open(expected, 'r').readlines(), open(actual_file, 'r').readlines()):
                    print(line)

            self.assertTrue(comparison)
            pass