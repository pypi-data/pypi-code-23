import unittest
from plotlog.selectlog import SelectLog

from argparse import Namespace
from os import makedirs
from os.path import isfile, isdir
from shutil import rmtree


class TestSelectLog(unittest.TestCase):
    def setUp(self):
        self.sl = SelectLog()
        self.put_log_dir = "log/"
        self.graph_save_dir = "graph/"
        self.log_date_type = 0
        self.args = Namespace(after=None, all=False, copy=False, input=None,
                              new=True, noshift=False, select=None,
                              setting='user.yml', slice=None)

    def test_arg_input(self):
        self.args = Namespace(after=None, all=False, copy=False,
                              input=["log/170101000000.csv", "log/170101120000.csv"],
                              new=True, noshift=False, select=None,
                              setting='user.yml', slice=None)
        paths = self.sl.get_logfile_paths(self.args, self.put_log_dir,
                                          self.graph_save_dir, self.log_date_type)
        self.assertEqual(paths[0], "log/170101000000.csv")
        self.assertEqual(paths[1], "log/170101120000.csv")
        self.assertTrue(isfile(paths[0]))
        self.assertTrue(isfile(paths[1]))

    def test_args_all(self):
        self.args = Namespace(after=None, all=True, copy=False, input=None,
                              new=True, noshift=False, select=None,
                              setting='user.yml', slice=None)
        paths = self.sl.get_logfile_paths(self.args, self.put_log_dir,
                                          self.graph_save_dir, self.log_date_type)

        for path in paths:
            self.assertTrue(isfile(path))

    def test_args_after(self):
        self.args = Namespace(after=["170102000000"], all=False, copy=False, input=None,
                              new=True, noshift=False, select=None,
                              setting='user.yml', slice=None)
        paths = self.sl.get_logfile_paths(self.args, self.put_log_dir,
                                          self.graph_save_dir, self.log_date_type)

        for path in paths:
            self.assertTrue(isfile(path))
        self.assertTrue("log/170102000000.csv" in paths)
        self.assertTrue("log/test1/170102180000.csv" in paths)
        self.assertTrue("log/test2/170103000000.csv" in paths)
        self.assertFalse("log/170101000000.csv" in paths)
        self.assertFalse("log/170101120000.csv" in paths)

    def test_args_select(self):
        self.args = Namespace(after=None, all=False, copy=False, input=None,
                              new=True, noshift=False,
                              select=["170102000000", "170103000000"],
                              setting='user.yml', slice=None)
        paths = self.sl.get_logfile_paths(self.args, self.put_log_dir,
                                          self.graph_save_dir, self.log_date_type)
        for path in paths:
            self.assertTrue(isfile(path))

        self.assertTrue("log/170102000000.csv" in paths)
        self.assertFalse("log/test1/170102180000.csv" in paths)
        self.assertTrue("log/test2/170103000000.csv" in paths)
        self.assertFalse("log/170101000000.csv" in paths)
        self.assertFalse("log/170101120000.csv" in paths)

    def test_args_new(self):
        if isdir("graph/"):
            rmtree("graph/")
        makedirs("graph/170101/170101000000")
        makedirs("graph/170102/170102000000")
        self.args = Namespace(after=None, all=False, copy=False, input=None,
                              new=True, noshift=False, select=None,
                              setting='user.yml', slice=None)
        paths = self.sl.get_logfile_paths(self.args, self.put_log_dir,
                                          self.graph_save_dir, self.log_date_type)
        for path in paths:
            self.assertTrue(isfile(path))
        self.assertFalse("log/170102000000.csv" in paths)
        self.assertTrue("log/test1/170102180000.csv" in paths)
        self.assertTrue("log/test2/170103000000.csv" in paths)
        self.assertFalse("log/170101000000.csv" in paths)
        self.assertTrue("log/170101120000.csv" in paths)


if __name__ == '__main__':
    unittest.main()
