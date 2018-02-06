from __future__ import absolute_import, print_function, unicode_literals
import unittest

from .testftp import testFTP
try:
    from .testsftp import testSFTP
except ImportError:
    pass
try:
    from .testhttpclient import testHTTPClient
except ImportError:
    pass
try:
    from .testhttpserver import testHTTPServer
except ImportError:
    pass
from .testlocal import testLocal
from .testmail import testMail
try:
    from .testsoap import testSOAP
except ImportError:
    pass
from .testzip import testZipfile

def suite():
    test_suite = unittest.TestSuite()

    test_suite.addTest(unittest.makeSuite(testFTP))
    test_suite.addTest(unittest.makeSuite(testSFTP))
    test_suite.addTest(unittest.makeSuite(testHTTPClient))
    test_suite.addTest(unittest.makeSuite(testHTTPServer))
    test_suite.addTest(unittest.makeSuite(testLocal))
    test_suite.addTest(unittest.makeSuite(testMail))
    test_suite.addTest(unittest.makeSuite(testSOAP))
    test_suite.addTest(unittest.makeSuite(testZipfile))

    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
