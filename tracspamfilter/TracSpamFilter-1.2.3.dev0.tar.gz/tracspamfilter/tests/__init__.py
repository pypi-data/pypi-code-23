# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

import unittest

import tracspamfilter.filters.tests
from tracspamfilter.tests import api, model


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(api.test_suite())
    suite.addTest(model.test_suite())
    suite.addTest(tracspamfilter.filters.tests.test_suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
