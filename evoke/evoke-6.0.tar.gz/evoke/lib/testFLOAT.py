""" Tests for Evoke FLOAT type.

Ian Howie Mackenzie July 2017 
"""

import unittest
from FLOAT import FLOAT


class TestFLOAT(unittest.TestCase):
    """ Test Evoke floating point numbers """

    def setUp(self):
        """ Set up any fixtures used by all tests. """

    def tearDown(self):
        """ Tidy up after testing. """

    def testDefaultCreation(self):
        """ check instance creation - no parameter defaults to 0 """
        x = FLOAT()
        self.assertEqual(x, 0)

    def testNumericCreation(self):
        """ check instance creation - numeric parameter """
        y = FLOAT(7.33)
        self.assertEqual(y, 7.33)

    def testInvalidCreation(self):
        """ check creation with invalid string input """
        y = FLOAT('hello')
        self.assertEqual(y, 0)

    def testStringCreation(self):
        """ check instance creation - string parameter """
        x = FLOAT('22.34')
        self.assertEqual(x, 22.34)

    def testSQLOutput(self):
        """ check quoted and unquoted output for sql """
        x = FLOAT('22.34')
        self.assertEqual(x.sql(), "'22.34'")
        self.assertEqual(x.sql(quoted=False), "22.34")

    def testSqlType(self):
        """ check sql type """
        a = FLOAT(1.23)
        self.assertEqual(a._v_mysql_type, "float")

    def testArithmeticOperations(self):
        """ check some arithmetic operations """
        x = FLOAT(22.34)
        y = FLOAT(7.89)
        self.assertGreater(x, y)

        x += y
        self.assertEqual(x, 30.23)

        x *= y  # x is no longer a FLOAT...
        self.assertEqual(x, 238.5147)

        self.assertEqual(FLOAT('2.6') / 2, FLOAT('1.3'))


if __name__ == '__main__':
    unittest.main()
