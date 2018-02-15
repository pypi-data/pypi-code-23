###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 4627 2017-07-10 02:26:31Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest
import doctest

import z3c.form.testing
import j01.form.testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt'),
        doctest.DocFileSuite('checker.txt'),
        # widgets
        doctest.DocFileSuite('dictionary.txt',
            setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('password.txt',
            setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('field.txt',
            setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=z3c.form.testing.outputChecker,
            ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
