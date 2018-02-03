"""Tests for our main byakugan CLI module."""

from subprocess import PIPE, Popen as popen
from unittest import TestCase

from byakugan import __version__ as VERSION


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(['byakugan', '-h'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:'.encode() in output)

        output = popen(['byakugan', '--help'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:'.encode() in output)


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = popen(['byakugan', '--version'], stdout=PIPE).communicate()[0]
        self.assertEqual(output.decode().strip(), VERSION)
