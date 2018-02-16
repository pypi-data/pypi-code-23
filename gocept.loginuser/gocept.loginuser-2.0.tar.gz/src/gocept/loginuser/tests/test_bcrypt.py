# encoding=utf-8
import AuthEncoding
# Run AuthEncoding tests against our BCrypt implementation
from AuthEncoding.tests.test_AuthEncoding import (  # noqa
    testGoodPassword, testBadPassword, testShortPassword, testLongPassword,
    testBlankPassword)


def test_bcrypt__BCryptScheme__1():
    """BCryptScheme is registered in AuthEncoding."""
    assert u'BCRYPT' in AuthEncoding.listSchemes()
