""" Tests for Evoke FLAG type.

Ian Howie Mackenzie July 2017
"""

import unittest
from FLAG import FLAG


class TestFLAG(unittest.TestCase):
    """ Test Evoke boolean flags """

    def setUp(self):
        """ Set up any fixtures used by all tests. """

    def tearDown(self):
        """ Tidy up after testing. """

    def testDefaultCreation(self):
        """ check instance creation - no parameter defaults to 0 """
        x = FLAG()
        self.assertFalse(x)
        self.assertEqual(str(x), 'N')

    def testNumericCreation(self):
        """ check instance creation - numeric parameter """
        x = FLAG(123)
        self.assertEqual(x, 1)
        y = FLAG(0)
        self.assertFalse(y)

    def testBooleanCreation(self):
        """ check instance creation - boolean parameter """
        x = FLAG(True)
        self.assertTrue(x)
        self.assertEqual(str(x), 'Y')
        y = FLAG(False)
        self.assertFalse(y)

    def testStringCreation(self):
        """ check instance creation - string parameter """
        x = FLAG("whatever")
        self.assertTrue(x)

    def testSQLOutput(self):
        """ check quoted and unquoted output for sql """
        x = FLAG(123)
        y = FLAG()
        self.assertEqual(x.sql(), "'Y'")
        self.assertEqual(y.sql(), "''")
        self.assertEqual(x.sql(quoted=False), "Y")

    def testBooleanOperations(self):
        """ check some boolean operations """
        x = FLAG("Y")
        y = FLAG()
        z = FLAG(1)
        self.assertTrue(x or y)
        self.assertTrue(x or False)
        self.assertTrue(x and not y)
        self.assertEqual(x, z)
        self.assertFalse(x != z)
        self.assertEqual(x, True)

    def testSqlType(self):
        """ check sql type """
        a = FLAG("Y")
        self.assertEqual(a._v_mysql_type, "char(1)")


if __name__ == '__main__':
    unittest.main()
