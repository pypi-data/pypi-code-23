#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `midtrans_python_rest_sdk` package."""


import unittest
from click.testing import CliRunner

from midtrans_python_rest_sdk import midtrans_python_rest_sdk
from midtrans_python_rest_sdk import cli


class TestMidtrans_python_rest_sdk(unittest.TestCase):
    """Tests for `midtrans_python_rest_sdk` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'midtrans_python_rest_sdk.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
