# -*- coding: utf-8 -*-
"""
Created on 2017-5-7

@author: cheng.li
"""

import sys
import unittest


class TestRunner(object):

    def __init__(self,
                 test_cases,
                 logger):
        self.suite = unittest.TestSuite()
        self.logger = logger
        for case in test_cases:
            tests = unittest.TestLoader().loadTestsFromTestCase(case)
            self.suite.addTests(tests)

    def run(self):
        self.logger.info('Python ' + sys.version)
        res = unittest.TextTestRunner(verbosity=3).run(self.suite)
        if len(res.errors) >= 1 or len(res.failures) >= 1:
            sys.exit(-1)
        else:
            sys.exit(0)
