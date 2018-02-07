from __future__ import print_function, unicode_literals
import time
import unittest
from datetime import datetime
from decimal import Decimal

from .. import ParseException
from ..field import (
    parse_int,
    unparse_int,
    parse_decimal,
    unparse_decimal,
    parse_boolean,
    unparse_boolean,
    parse_string,
    unparse_string,
    parse_date,
    unparse_date,
    parse_constant,
    unparse_constant,
    parse_enum,
    unparse_enum,
    field,
    int_field,
    decimal_field,
    string_field,
    constant_field,
    enum_field,
    EMAIL_STRING,
    URL_STRING,
)

class testIntField(unittest.TestCase):

    def test_parse_valid(self):
        output = parse_int('10')
        self.assertEqual(output, 10)

    def test_parse_invalid(self):
        self.assertRaises(ParseException, parse_int, 'wibble')
        output = parse_int('wibble', required = False)
        self.assertEqual(output, None)

    def test_parse_nonzero(self):
        output = parse_int(-2, nonzero = True)
        self.assertEqual(output, -2)

    def test_parse_nonzero_fail(self):
        self.assertRaises(ParseException, parse_int, 0, nonzero = True)

    def test_parse_positive(self):
        output = parse_int(2, positive = True)
        self.assertEqual(output, 2)

    def test_parse_positive_fail(self):
        self.assertRaises(ParseException, parse_int, -2, positive = True)

    def test_unparse_valid(self):
        output = unparse_int(10)
        self.assertEqual(output, '10')

    def test_unparse_with_length(self):
        output = unparse_int(10, 5)
        self.assertEqual(output, '00010')

    def test_unparse_with_length_spaces(self):
        output = unparse_int(10, 5, filler = ' ')
        self.assertEqual(output, '   10')

class testDecimalField(unittest.TestCase):

    def test_parse(self):
        output = parse_decimal('10.48')
        self.assertEqual(output, Decimal('10.48'))

    def test_parse_invalid(self):
        self.assertRaises(ParseException, parse_decimal, 'wibble')
        output = parse_decimal('wibble', required = False)
        self.assertEqual(output, None)

    def test_parse_precision_min(self):
        self.assertRaises(
            ParseException,
            parse_decimal, '10.48', precision = 3,
       )

    def test_parse_precision_max(self):
        self.assertRaises(
            ParseException,
            parse_decimal, '10.48', precision = 1,
       )

    def test_parse_min_precision(self):
        self.assertRaises(
            ParseException,
            parse_decimal, '10.48', min_precision = 3,
       )

    def test_parse_max_precision(self):
        self.assertRaises(
            ParseException,
            parse_decimal, '10.48', max_precision = 1,
       )

    def test_unparse(self):
        output = unparse_decimal(10.48)
        self.assertEqual(output, '10.48')

    def test_unparse_invalid(self):
        self.assertRaises(ParseException, unparse_decimal, 'wibble')

    def test_unparse_length_and_precision(self):
        output = unparse_decimal(10.48, 5, 1)
        self.assertEqual(output, '010.5')

    def test_unparse_length_spaces(self):
        output = unparse_decimal(10.48, 7, filler = ' ')
        self.assertEqual(output, '  10.48')

class testBooleanField(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(True, parse_boolean('Y', positive = 'y'))
        self.assertEqual(
            False, parse_boolean('False', negative = 'false')
       )

    def test_parse_fail(self):
        self.assertRaises(ParseException, parse_boolean, 'wibble')
        self.assertRaises(
            ParseException,
            parse_boolean,
            'Yes',
            positive = 'yes',
            ignore_case = False
       )

    def test_unparse(self):
        self.assertEqual('1', unparse_boolean(True))
        self.assertEqual('N', unparse_boolean(False, negative = 'N'))

class testStringField(unittest.TestCase):

    def test_parse(self):
        output = parse_string('wibble')
        self.assertEqual(output, 'wibble')

    def test_parse_fail(self):
        self.assertRaises(ParseException, parse_string, '')
        output = parse_string('', required = False)
        self.assertEqual(output, '')

    def test_unparse(self):
        output = unparse_string('wibble')
        self.assertEqual(output, 'wibble')

    def test_unparse_with_length(self):
        output = unparse_string('wibble', 8)
        self.assertEqual(output, '  wibble')

    def test_unparse_left_justify(self):
        output = unparse_string('wibble', 8, justify = 'left')
        self.assertEqual(output, 'wibble  ')

    def test_unparse_center_justify(self):
        output = unparse_string('wibble', 8, justify = 'center')
        self.assertEqual(output, ' wibble ')

    def test_unparse_alt_filler(self):
        output = unparse_string('wibble', 8, filler = '.')
        self.assertEqual(output, '..wibble')

    def test_unparse_truncate(self):
        output = unparse_string('wibble', 3)
        self.assertEqual(output, 'wib')

class testStringMatches(unittest.TestCase):
    def test_parse_email(self):
        output = parse_string(
            'wibble@bob.com', match = EMAIL_STRING
       )
        self.assertNotEqual(output, None)

    def test_parse_url(self):
        output = parse_string(
            'http://www.xengamous.com/simpleformats/',
            match = URL_STRING,
       )
        self.assertNotEqual(output, None)

        output = parse_string(
            'http://www.xengamous.com:8080/',
            match = URL_STRING,
       )
        self.assertNotEqual(output, None)

        output = parse_string(
            'ftp://xengamous.com:21/',
            match = URL_STRING,
       )
        self.assertNotEqual(output, None)

    def test_parse_email_fail(self):
        self.assertRaises(
            ParseException,
            parse_string, 'wibble', match = EMAIL_STRING,
       )
        self.assertRaises(
            ParseException,
            parse_string, 'wibble@bob', match = EMAIL_STRING,
       )

        def test_parse_url_fail(self):
            self.assertRaises(
                ParseException,
                parse_string,
                'www.xenogamous.com',
                match = EMAIL_STRING,
           )

    def test_unparse_email(self):
        output = unparse_string(
            'wibble@bob.com', match = EMAIL_STRING
       )
        self.assertEqual(output, 'wibble@bob.com')

    def test_unparse_url(self):
        output = unparse_string(
            'http://www.xenogamous.com/', match = URL_STRING
       )
        self.assertEqual(output, 'http://www.xenogamous.com/')

    def test_unparse_email_fail(self):
        self.assertRaises(
            ParseException,
            unparse_string, 'wibble@bob', match = EMAIL_STRING,
       )

    def test_unparse_url_fail(self):
        self.assertRaises(
            ParseException,
            unparse_string, 'xenogamous.com', match = URL_STRING,
       )

class testDateField(unittest.TestCase):
    def test_parse(self):
        output = parse_date('2015-04-01 13:00:56', '%Y-%m-%d %H:%M:%S' )
        self.assertEqual(
            output,
            datetime(2015, 4, 1, 13, 0, 56)
       )

    def test_parse_invalid(self):
        self.assertRaises(
            ParseException,
            parse_date, 'wibble@bob', '%Y-%m-%d %H:%M:%S'
       )

    def test_unparse(self):
        output = unparse_date(
            datetime(2015, 4, 1, 14, 0, 15),
            fmt = '%Y-%m-%d %H:%M:%S',
       )
        self.assertEqual(output, '2015-04-01 14:00:15')

    def test_unparse_invalid(self):
        self.assertRaises(ParseException, unparse_date, 'not a date')

class testConstantField(unittest.TestCase):
    def test_constant(self):
        output = parse_constant('aaaa', 'aaaa')
        self.assertEqual(output, 'aaaa')
        self.assertRaises(ParseException, parse_constant, 'aaaa', 'bbbb')

        output = unparse_constant(None, 4, 'aaaa')
        self.assertEqual(output, 'aaaa')

        obj = constant_field(constant = 'aaaa')
        output = obj.parse('aaaa')
        self.assertEqual(output, 'aaaa')
        self.assertRaises(ParseException, obj.parse, ('bbbb'))

        output = obj.unparse(None)
        self.assertEqual(output, 'aaaa')

class testEnumField(unittest.TestCase):
    def test_enum(self):
        output = parse_enum('aaaa', ('aaaa', 'bbbb'))
        self.assertEqual(output, 'aaaa')
        self.assertRaises(ParseException, parse_enum, 'aaaa', ('bbbb',))
        output = parse_enum('aaaa', ('AaAa',), ignore_case=True)
        self.assertEqual(output, 'aaaa')

        output = unparse_enum('bbbb', 4, ('aaaa', 'bbbb'))
        self.assertEqual(output, 'bbbb')

        obj = enum_field(options = ('aaaa', 'bbbb'))
        output = obj.parse('bbbb')
        self.assertEqual(output, 'bbbb')
        self.assertRaises(ParseException, obj.parse, 'cccc')

        output = obj.unparse('aaaa')
        self.assertEqual(output, 'aaaa')

class testFieldObject(unittest.TestCase):
    def test_field(self):
        fobj = field()
        self.assertEqual(fobj.get_field('0123456789'), '0123456789')

        fobj = field(0, 4)
        self.assertEqual(fobj.get_field('0123456789'), '0123')
        self.assertRaises(ParseException, fobj.get_field, '012')

if __name__ == '__main__':
    unittest.main()
