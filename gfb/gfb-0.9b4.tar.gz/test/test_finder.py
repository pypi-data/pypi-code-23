import unittest
import os
import configparser
from gfb.git import Credentials, BranchFinder
from gfb.git import AuthenticationError, BadRepoError
from gfb.git import LocalRepoFinder, BranchSelector


class TestGithub(unittest.TestCase):

    def _test_creds(self):
        try:
            user = os.environ['TEST_USER']
            pwd = os.environ['TEST_PASS']
        except KeyError:
            self.fail("Missing TEST_USER & TEST_PASS env vars!")
        else:
            return (user, pwd)

    def test_find_branch(self):
        user, pwd = self._test_creds()
        creds = Credentials('apple/swift', username=user, password=pwd)
        finder = BranchFinder(creds)
        branches = finder.find_branch(r'^stdlib*')
        self.assertEqual(len(branches), 5)

    def test_bad_creds(self):
        creds = Credentials("apple/swift", username='no', password='body')
        finder = BranchFinder(creds)
        try:
            branches = finder.find_branch(r'^stdlib*')
            self.assertTrue(len(branches) > 0)
        except AuthenticationError as ae:
            self.assertIsInstance(ae, AuthenticationError)
        else:
            self.fail()

    def test_bad_repo(self):
        user, pwd = self._test_creds()
        creds = Credentials("thisisnot/arepo", username=user, password=pwd)
        finder = BranchFinder(creds)
        try:
            branches = finder.find_branch(r'^stdlib*')
            self.assertTrue(len(branches) == 0)
        except BadRepoError as ae:
            self.assertIsInstance(ae, BadRepoError)
        else:
            self.fail()

    def test_url_name(self):
        repo = LocalRepoFinder('./')
        test_config = """
        [remote "origin"]
        url = https://github.com/barnardn/gfb.git
        """
        parser = configparser.ConfigParser()
        parser.read_string(test_config)
        name = repo.get_repo_name(parser)
        if name[0] == '/':
            name = name[1:]
        self.assertEqual(name, 'barnardn/gfb')

    def test_git_url_name(self):
        repo = LocalRepoFinder('./')
        test_config = """
        [remote "origin"]
        url = git@github.com:barnardn/gfb.git
        """
        parser = configparser.ConfigParser()
        parser.read_string(test_config)
        name = repo.get_repo_name(parser)
        self.assertEqual(name, 'barnardn/gfb')

        test_config = """
        [remote "origin"]
        url = git@github.com:/barnardn/gfb.git
        """
        parser = configparser.ConfigParser()
        parser.read_string(test_config)
        name = repo.get_repo_name(parser)
        self.assertEqual(name, 'barnardn/gfb')

    def test_find_local_repo_dir(self):
        repo = LocalRepoFinder('/home/barnard/projects/gfb/test')
        result = repo.find_local_repo_dir()
        self.assertTrue(result)
        self.assertEqual(repo.repo_dir, '/home/barnard/projects/gfb/.git')

    def test_no_local_repo(self):
        repo = LocalRepoFinder('/home/barnard/projects/')
        result = repo.find_local_repo_dir()
        self.assertFalse(result)

    def test_local_repo(self):
        repo = LocalRepoFinder('/home/barnard/projects/gfb/test')
        result = repo.local_repo_name()
        if result[0] == '/':
            result = result[1:]
        self.assertEqual(result, 'barnardn/gfb')


class TestBranchSelector(unittest.TestCase):

    def test_selector_no_local(self):
        branches = ['one', 'two', 'three', 'four', 'five']
        selector = BranchSelector(branches, False)
        result = selector.choose_branch()
        self.assertIsNone(result)

    def test_selector_local(self):
        branches = ['one', 'two', 'three', 'four', 'five']
        selector = BranchSelector(branches, True)
        print("Pick Branch Number 2\n")
        result = selector.choose_branch()
        self.assertEqual('two', result)

    def test_select_exit(self):
        branches = ['one', 'two', 'three', 'four', 'five']
        selector = BranchSelector(branches, True)
        print("Select 'X' to exit without selection\n")
        result = selector.choose_branch()
        self.assertIsNone(result)

    def test_no_results(self):
        selector = BranchSelector([], True)
        result = selector.choose_branch()
        self.assertIsNone(result)
