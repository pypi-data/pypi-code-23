import unittest
import os
import shutil
import sys
from subprocess import call
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chestella.chestella import create_parser
from chestella.project.Project import Project
from test_args import CLITestCase


class TestDirectoryTree(CLITestCase):

    ROOT = "{}/test_project/".format(os.getcwd())
    # ROOT = "test_project/"

    def setUp(self):
        self.args = self.parser.parse_args("init {}".format(self.ROOT).split())
        self.project = Project(self.args.path)

    def test_creates_directory_tree(self):
        paths = [self.ROOT+"src/",
                 self.ROOT+"bin/",
                 self.ROOT+"obj/",
                 self.ROOT+"Makefile"]
        for path in paths:
            exists = os.path.exists(path)
            self.assertTrue(exists)

    def test_make_compiles(self):
        ret = call("make -C {}".format(self.ROOT).split())
        self.assertEqual(ret, 0)

    def test_executes(self):
        call("make -C {}".format(self.ROOT).split())
        ret = call("{name}/bin/{name}".format(name=self.project.name).split())
        self.assertEqual(ret, 0)

    def tearDown(self):
        try:
            shutil.rmtree(self.ROOT)
        except Exception as e:
            pass


if __name__ == "__main__":
    unittest.main()
