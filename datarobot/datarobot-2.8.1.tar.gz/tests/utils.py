import unittest
import contextlib
import warnings
import re
import sys

from datarobot.client import set_client
from datarobot.rest import RESTClientObject


class SDKTestcase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_client(None)
        c = RESTClientObject(auth='t-token', endpoint='https://host_name.com')
        set_client(c)

    @classmethod
    def tearDownClass(cls):
        set_client(None)


@contextlib.contextmanager
def warns(*categories):
    """Assert warnings are raised in a block, analogous to pytest.raises."""
    with warnings.catch_warnings(record=True) as messages:
        yield messages
    assert tuple(message.category for message in messages) == categories


def assert_raised_regex(exc_info, regexp):
    """
    Until pytest 2.10 when this gets implemented as a method of exc_info,
    we will provide this assertion.

    This is the exact implementation that has already been merged to pytest

    Parameters
    ----------
    exc_info : pytest.ExceptionInfo
    regexp

    Returns
    -------

    """
    if not re.search(regexp, str(exc_info.value)):
        assert 0, "Pattern '{0!s}' not found in '{1!s}'".format(
            regexp, exc_info.value
        )
    return True


def assert_equal_py2(this, that):
    """Assert that arguments are equal on Python 2.

    This function does nothing on Python 3.
    """
    if sys.version_info < (3, 0):
        assert this == that


def assert_equal_py3(this, that, message=''):
    """Assert that arguments are equal on Python 3.

    This function does nothing on Python 2.
    """
    if sys.version_info >= (3, 0):
        assert this == that
