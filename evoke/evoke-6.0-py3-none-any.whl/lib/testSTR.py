""" Tests for Evoke string types (STR,TAG, and CHAR).

Ian Howie Mackenzie July 2017
"""

import unittest
from STR import STR, TAG, CHAR


class TestSTR(unittest.TestCase):
    """ Test Evoke strings """

    def setUp(self):
        """ Set up any fixtures used by all tests. """

    def tearDown(self):
        """ Tidy up after testing. """

    def testDefaultCreation(self):
        """ check instance creation - no parameter defaults to 0 """
        x = STR()
        self.assertEqual(x, '')

    def testStringCreation(self):
        """ check instance creation - string parameter """
        y = TAG('hello')
        self.assertEqual(y, "hello")

    def testInvalidCreation(self):
        """ check instance creation - non-string parameter """
        z = STR(None)
        self.assertEqual(z, '')
        z = STR('')
        self.assertEqual(z, '')
        z = STR(False)
        self.assertEqual(z, '')
        z = STR(True)
        self.assertEqual(z, '')
        z = STR(123)
        self.assertEqual(z, '')

    def testSQLOutput(self):
        """ check quoted and unquoted output for sql """

        x = TAG('abc' * 100)
        y = TAG(x[:4])
        z = CHAR('goodbye')
        self.assertEqual(len(x.sql(quoted=False)), 255)
        self.assertEqual(y.sql(), "'abca'")
        self.assertEqual(z.sql(), "'g'")
        self.assertEqual(z.sql(quoted=False), "g")

    def testSqlType(self):
        """ check sql types """
        a = STR("")
        b = TAG("")
        c = CHAR("")
        self.assertEqual(a._v_mysql_type, "mediumtext")
        self.assertEqual(b._v_mysql_type, "varchar(255)")
        self.assertEqual(c._v_mysql_type, "char(1)")

    def testComparison(self):
        """ check comparison """
        x = TAG("abcd")
        y = STR("efg")
        self.assertTrue(x < y)

    def testTruth(self):
        """ check truth """
        x = STR()
        y = TAG('hello')
        self.assertFalse(x)
        self.assertTrue(y)

    def testOperators(self):
        """ check boolean operators """
        x = STR("hello")
        y = STR("Y")
        z = STR()
        self.assertTrue(x or z)
        self.assertTrue(x and y and not z)


if __name__ == '__main__':
    unittest.main()
