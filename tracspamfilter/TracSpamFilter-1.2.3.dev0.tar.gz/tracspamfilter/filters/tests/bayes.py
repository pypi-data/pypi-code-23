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

from trac.test import EnvironmentStub, Mock, MockRequest

from tracspamfilter.filtersystem import FilterSystem
from tracspamfilter.tests.model import reset_db


class BayesianFilterStrategyTestCase(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub(enable=[BayesianFilterStrategy])
        self.env.config.set('spam-filter', 'bayes_karma', '10')
        FilterSystem(self.env).upgrade_environment()

        self.strategy = BayesianFilterStrategy(self.env)

    def tearDown(self):
        reset_db(self.env)

    def test_karma_calculation_unsure(self):
        bayes.Hammie = lambda x: Mock(score=lambda x: .5,
                                      bayes=Mock(nham=1000, nspam=1000))

        req = MockRequest(self.env)
        self.assertEquals(None, self.strategy.test(req, 'John Doe', 'Spam',
                                                   '127.0.0.1'))

    def test_karma_calculation_negative(self):
        bayes.Hammie = lambda x: Mock(score=lambda x: .75,
                                      bayes=Mock(nham=1000, nspam=1000))

        req = MockRequest(self.env)
        points, reasons, args = \
            self.strategy.test(req, 'John Doe', 'Spam', '127.0.0.1')
        self.assertEquals(-5, points)

    def test_karma_calculation_positive(self):
        bayes.Hammie = lambda x: Mock(score=lambda x: .25,
                                      bayes=Mock(nham=1000, nspam=1000))

        req = MockRequest(self.env)
        points, reasons, args = \
            self.strategy.test(req, 'John Doe', 'Spam', '127.0.0.1')
        self.assertEquals(5, points)

    def test_classifier_untrained(self):
        req = MockRequest(self.env)
        self.assertEqual(None, self.strategy.test(req, 'John Doe', 'Hammie',
                                                  '127.0.0.1'))

    def test_classifier_basics(self):
        req = MockRequest(self.env)
        self.env.config.set('spam-filter', 'bayes_min_training', '1')
        self.strategy.train(req, 'John Doe', 'Spam spam spammie', '127.0.0.1',
                            True)
        self.strategy.train(req, 'John Doe', 'Ham ham hammie', '127.0.0.1',
                            False)

        points, reasons, args = \
            self.strategy.test(req, 'John Doe', 'Hammie', '127.0.0.1')
        self.assertGreater(points, 0, 'Expected positive karma')
        points, reasons, args = \
            self.strategy.test(req, 'John Doe', 'Spam', '127.0.0.1')
        self.assertLess(points, 0, 'Expected negative karma')


try:
    from tracspamfilter.filters import bayes
    from tracspamfilter.filters.bayes import BayesianFilterStrategy
except ImportError:
    # Skip tests if SpamBayes isn't installed
    class BayesianFilterStrategyTestCase(object):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BayesianFilterStrategyTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
