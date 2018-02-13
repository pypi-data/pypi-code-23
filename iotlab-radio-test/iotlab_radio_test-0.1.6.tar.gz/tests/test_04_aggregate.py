import filecmp
import os
import tempfile
import unittest
from difflib import unified_diff

from iotlab_radio_test.cli import aggregate_stability_main
from iotlab_radio_test.cli import aggregate_avg_main

from iotlab_radio_test.config import get_config_from_yaml
from distutils.dir_util import copy_tree

from iotlab_radio_test.start import get_api


class UnitTest04Aggregate(unittest.TestCase):
    def _from_data_(self, name, main_func):
        input_experiments_dir = os.path.join('tests', 'test_data_04_aggregate', 'tests_experiments')
        expected_output_dir = os.path.join('tests', 'test_data_04_aggregate', 'tests_experiments', name, 'parsed')
        temp_experiments_dir = tempfile.mkdtemp()
        temp_output_dir = os.path.join(temp_experiments_dir, name, 'parsed')

        copy_tree(input_experiments_dir, temp_experiments_dir)

        config = get_config_from_yaml()
        config.node_list = [4, 5, 9]
        config.radio.channel_list = [11, 12]
        config.site = 'lille'

        main_func(config, temp_experiments_dir, temp_output_dir, [85471, 85529], name)

        for file in os.listdir(expected_output_dir):
            actual_file = os.path.join(temp_output_dir, file)
            self.assertTrue(os.path.exists(actual_file))
            expected = os.path.join(expected_output_dir,file)

            comparison = filecmp.cmp(expected, actual_file, False)

            if not comparison:
                print(file)
                for line in unified_diff(open(expected,'r').readlines(),open(actual_file,'r').readlines()):
                    print(line)

            self.assertTrue(comparison)
            pass

    def test_from_data_avg(self):
        self._from_data_('2_exps_avg', aggregate_avg_main)

    def test_from_data_stability(self):
        self._from_data_('2_exps_stability', aggregate_stability_main)
