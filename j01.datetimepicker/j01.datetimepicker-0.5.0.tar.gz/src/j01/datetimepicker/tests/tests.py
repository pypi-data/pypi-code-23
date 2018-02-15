###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 4755 2018-02-15 05:06:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest
import doctest

import z3c.form.testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt'),
        doctest.DocFileSuite('../README.txt',
         setUp=z3c.form.testing.setUp,
         tearDown=z3c.form.testing.tearDown,
         optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
         ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
