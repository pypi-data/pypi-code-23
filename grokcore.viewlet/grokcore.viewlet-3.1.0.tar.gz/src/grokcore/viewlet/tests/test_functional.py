##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import re
import unittest
import doctest
import grokcore.viewlet
import zope.testbrowser.wsgi
import zope.app.wsgi.testlayer

from pkg_resources import resource_listdir
from zope.testing import renormalizing


class Layer(
        zope.testbrowser.wsgi.TestBrowserLayer,
        zope.app.wsgi.testlayer.BrowserLayer):
    pass

layer = Layer(grokcore.viewlet, allowTearDown=True)


checker = renormalizing.RENormalizing([
    # Accommodate to exception wrapping in newer versions of mechanize
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
    ])


def suiteFromPackage(name):
    layer_dir = 'functional'
    files = resource_listdir(__name__, '{}/{}'.format(layer_dir, name))
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'grokcore.viewlet.tests.%s.%s.%s' % (
            layer_dir, name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            checker=checker,
            extraglobs=dict(getRootFolder=layer.getRootFolder,),
            optionflags=(
                doctest.ELLIPSIS +
                doctest.NORMALIZE_WHITESPACE +
                doctest.REPORT_NDIFF +
                renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2))
        test.layer = layer

        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['viewlet']:
        suite.addTest(suiteFromPackage(name))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
