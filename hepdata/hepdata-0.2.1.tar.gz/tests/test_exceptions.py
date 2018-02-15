#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_exceptions
----------------------------------

Tests for `hepdata.exceptions` module.
"""

import unittest

from hepdata import exceptions


class TestExceptions(unittest.TestCase):

    def test_app_code(self):
        exc = exceptions.HEPError(code=8)
        self.assertEqual(
            exc.__str__(),
            "Error 8: IP address not whitelisted",
        )

    def test_server_code(self):
        exc = exceptions.HEPError(code=500)
        self.assertEqual(
            exc.__str__(),
            "HTTP 500",
        )


if __name__ == '__main__':
    unittest.main()
