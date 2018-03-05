""" Tests for Evoke INT type.

Christopher J Hurst and Ian Howie Mackenzie July 2017 
"""

import unittest
from INT import INT, SMALLINT, TINYINT


class TestINT(unittest.TestCase):
    """ Test Evoke integers """

    def setUp(self):
        """ Set up any fixtures used by all tests. """

    def tearDown(self):
        """ Tidy up after testing. """

    def testDefaultCreation(self):
        """ check instance creation - no parameter defaults to 0 """
        x = INT()
        self.assertEqual(x, 0)

    def testNumericCreation(self):
        """ check instance creation - numeric parameter """
        x = INT(10)
        self.assertEqual(x, 10)

    def testNegativeNumericCreation(self):
        """ check instance creation - negative integer parameter """
        x = INT(-10000)
        self.assertEqual(x, -10000)

    def testStringCreation(self):
        """ check instance creation - string parameter """
        x = INT('22')
        self.assertEqual(x, 22)

    def testSQLOutput(self):
        """ check quoted and unquoted output for sql """
        x = INT('22')
        self.assertEqual(x.sql(), "'22'")
        self.assertEqual(x.sql(quoted=False), "22")

    def testCreateInvalid(self):
        """ check creation with invalid string input """
        y = INT('hello')
        self.assertEqual(y, 0)

    def testArithmeticOperations(self):
        """ check some arithmetic operations """
        x = INT(22)
        y = INT(7)
        self.assertGreater(x, y)

        x += y
        self.assertEqual(x, 29)

        x *= y
        # x is no longer an INT...
        self.assertEqual(x, 203)
        self.assertEqual(196, -(y - x))

        y += 8
        self.assertEqual(y, 15)

    def testHashedEquivalence(self):
        """ test hashed equivalence """
        self.assertEqual(INT(23), INT(23))
        self.assertEqual(INT(23), 23)

    def testForcedFloordiv(self):
        """ Test division always floors, unlike Python3 default """
        self.assertEqual(INT(9) / 4, 2)
        self.assertEqual(INT(9) // 4, 2)
        self.assertEqual(9 / INT(4), 2)
        self.assertEqual(9 // INT(4), 2)

    def testSqlType(self):
        """ check sql type """
        a = TINYINT(123)
        b = SMALLINT(456)
        c = INT(789)
        self.assertEqual(a._v_mysql_type, "tinyint")
        self.assertEqual(b._v_mysql_type, "smallint")
        self.assertEqual(c._v_mysql_type, "int(11)")


if __name__ == '__main__':
    unittest.main()
