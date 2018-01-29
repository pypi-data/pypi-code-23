import unittest
import os
import shutil
import sys
from subprocess import call
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chestella.chestella import create_parser
from chestella.project.Project import Project
from test_directory_tree import TestDirectoryTree

class TestRelativePath(TestDirectoryTree):

    ROOT = "test_project/"

if __name__ == "__main__":
    unittest.main()
