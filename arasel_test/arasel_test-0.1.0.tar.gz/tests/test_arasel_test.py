#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `arasel_test` package."""
import csv
import unittest

import os
from click.testing import CliRunner
import numpy
import dill


from arasel_test.arasel_etl import AraselETL
from arasel_test import cli
from arasel_test.fields import CustomerField

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class TestArasel_test(unittest.TestCase):
    """Tests for `arasel_test` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.orders_csv = os.path.join(THIS_DIR, '../data/orders.csv')
        self.model_path = os.path.join(THIS_DIR, '../data/model.dill')
        self.customers_clvs_output = os.path.join(THIS_DIR, '../data/customer_clvs.csv')

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_clv_predictions(self):
        """Test something."""
        with open(self.model_path, 'rb') as f:
            model = dill.dill.load(f)

        etl = AraselETL(self.orders_csv, model)

        customer_clvs = etl.customer_clvs

        clvs_size = len(customer_clvs)

        self.assertTrue(clvs_size > 0, msg="No Customer Lifetime Values returned")

        etl.to_csv(self.customers_clvs_output)

        with open(self.customers_clvs_output) as f:
            reader = csv.DictReader(f)

            self.assertEquals(set(reader.fieldnames), set(CustomerField.fields()))

            num_lines = sum(1 for line in reader)
            self.assertEquals(clvs_size, num_lines)


    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'arasel_test.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output


if __name__ == '__main__':
    unittest.main()
