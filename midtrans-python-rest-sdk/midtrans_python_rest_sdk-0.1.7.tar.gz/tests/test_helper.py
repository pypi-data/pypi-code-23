import logging
import re
import unittest

from midtrans_python_rest_sdk import midtrans_python_rest_sdk as midtrans


# Logging
logging.basicConfig(level=logging.INFO)

# Credential
server_key = ""

# Set credential for default api
midtrans.configure(server_key=server_key)


def assert_regex_matches(test, s, regex):
    test.assertTrue(re.compile(regex).search(s))
