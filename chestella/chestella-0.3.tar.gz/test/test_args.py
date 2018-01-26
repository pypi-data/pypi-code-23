"""Tests for the CLI"""
import unittest
import os
import shutil
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chestella.chestella import create_parser
from chestella.project.Project import Project


class CLITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = create_parser()


class TestArgs(CLITestCase):
    """Testing the CLI"""

    def setUp(self):
        self.args = ["init", "some_project", "extra_arg"]

    def test_init_parses_correctly(self):
        args = self.parser.parse_args(self.args[:2])
        self.assertEqual(args.path, "some_project")

    def test_init_does_not_accept_more_than_one_arg(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(self.args)

    def test_init_does_not_accept_less_than_one_arg(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args()

    def test_just_init_will_not_work(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(self.args[:1])

    def test_create_project(self):
        args = self.parser.parse_args(self.args[:2])
        p = Project(args.path)
        self.assertIsNotNone(p)

    def test_create_project_with_right_name(self):
        args = self.parser.parse_args(self.args[:2])
        p = Project(args.path)
        self.assertEqual(p.path, "some_project")
        self.assertEqual(p.name, "some_project")

    def tearDown(self):
        try:
            shutil.rmtree("some_project")
        except Exception as e:
            pass


if __name__ == "__main__":
    unittest.main()
