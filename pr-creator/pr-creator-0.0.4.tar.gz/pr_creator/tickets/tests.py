import unittest
from .branches import simple_slugify, branch_name
from collections import namedtuple


class TestSlugifier(unittest.TestCase):

    def test_stripped(self):
        self.assertEqual(simple_slugify('  foo '), 'foo')

    def test_replaced(self):
        self.assertEqual(simple_slugify('foo bar'), 'foo-bar')

    def test_lowered(self):
        self.assertEqual(simple_slugify('FOO BaR'), 'foo-bar')

    def test_all(self):
        self.assertEqual(simple_slugify('   FOO BaR '), 'foo-bar')


class TestBranchName(unittest.TestCase):

    def test_formatted(self):
        Args = namedtuple('Args', ['ticket_type', 'ticket_id', 'ticket_name'])
        args = Args('feature', 'NAV-5050', 'Do a thing')

        self.assertEqual(branch_name(args), 'feature/NAV-5050-do-a-thing')
