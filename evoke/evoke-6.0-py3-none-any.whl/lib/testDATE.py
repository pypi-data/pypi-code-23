""" Tests for Evoke DATE type.

Ian Howie Mackenzie July 2017 
"""

import unittest
from DATE import DATE


class TestDATE(unittest.TestCase):
    """ Test Evoke  """

    def setUp(self):
        """ Set up any fixtures used by all tests. """

    def tearDown(self):
        """ Tidy up after testing. """

    def testDefaultCreation(self):
        """ check instance creation - no parameter defaults to 0 """
        x = DATE()
        self.assertTrue(x.valid)  # should be set to current datetime

    def testInvalidCreatione(self):
        """ check instance creation from invalid parameters """
        y = DATE('22/13/1951')
        self.assertFalse(
            y.valid)  # should be set to 1/1/1900 with .valid set False
        d = DATE('')
        self.assertFalse(d.valid)

    def testStringCreation(self):
        """ check instance creation - string parameter """
        x = DATE('22/8/1961')
        self.assertTrue(x.valid)

    def testComparisons(self):
        """ check the comparison operators """
        x = DATE('3/10/7')
        y = DATE('20071003')
        z = DATE()
        self.assertEqual(x, y)
        self.assertTrue(z > y)
        self.assertTrue(y >= x)

    def testDateArithmetic(self):
        """ check date arithmetic """
        d = DATE('22/8/1961').add(
            years=46, months=5, days=1, hours=1, minutes=2, seconds=59)
        d.add(years=1, hours=25, minutes=61, seconds=3)
        dd = DATE('24/1/2008').add(hours=3, minutes=4, seconds=2)
        self.assertEqual(dd, d)

    def testTimes(self):
        """ check time handling  """
        d = DATE('24/10/2013 14:18')
        self.assertEqual(d.time(), "24/10/2013 14:18")
        self.assertEqual(d.time(sec=True), "24/10/2013 14:18:00")
        d = DATE('24/10/2013 14:18:23')
        self.assertEqual(d.time(sec=True), "24/10/2013 14:18:23")

    def testSQLOutput(self):
        """ check quoted and unquoted output for sql """
        d = DATE('12/4/1936')
        dt = DATE('1/2/03 14:04:27')
        self.assertEqual(d.sql(time=False), "'1936-04-12'")
        self.assertEqual(d.sql(time=False, quoted=False), "1936-04-12")
        self.assertEqual(dt.sql(), "'2003-02-01 14:04:27'")

    def testSqlType(self):
        """ check sql type """
        a = DATE()
        self.assertEqual(a._v_mysql_type, "datetime")


if __name__ == '__main__':
    unittest.main()
