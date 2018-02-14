from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import os
from pyshifu.util.helper import Helper


class TestHelper(unittest.TestCase):
    def setUp(self):
        self._current_script_path = os.path.dirname(os.path.abspath(__file__))

    def test_get_current_path(self):
        status, result = Helper.run_shell(['pwd', ])
        self.assertEqual(Helper.get_current_path(), result.strip())

    def test_run_shell(self):
        status, result = Helper.run_shell(['pwd', ])
        self.assertEqual(result.strip(), Helper.get_current_path())

    def test_get_environment_variable(self):
        current_path = Helper.get_environment_variable("PWD")
        if current_path is not None:
            self.assertEqual(Helper.get_environment_variable("PWD"), Helper.get_current_path())

    def test_get_shifu_home(self):
        self.assertEqual(Helper.get_shifu_home().split('/')[-1], "pyshifu")

    def test_set_os_environment(self):
        Helper.set_os_environment("SHIFU_HOME", "wu")
        self.assertEqual(Helper.get_environment_variable("SHIFU_HOME"), "wu")

    def test_list_files_in_directory(self):
        self.assertEqual(len(Helper.list_files_in_directory(Helper.get_shifu_home(), True, "py")), 2)


if __name__ == '__main__':
    unittest.main()
