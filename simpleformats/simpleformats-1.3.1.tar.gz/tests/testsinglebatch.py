from decimal import Decimal
import unittest

from .. import (
    int_field,
    decimal_field,
    string_field,
    date_field,
    delimited_record,
    record_batch,
    ParseException,
)

parsed_record = {
    u'_type': 1,
    u'_line': 1,
    u'first': u'wibble',
    u'second': Decimal( '32.56' ),
    u'third': u'bob,fred',
    u'fourth': 100,
    u'fifth': u'alpha,beta',
}

record_format = delimited_record(
    ( u'_type', int_field() ),
    ( u'_line', int_field() ),
    ( u'first', string_field() ),
    ( u'second', decimal_field() ),
    ( u'third', string_field() ),
    ( u'fourth', int_field() ),
    ( u'fifth', string_field() ),
)

raw_record = u'1,1,wibble,32.56,"bob,fred",100,"alpha,beta"'
invalid_record = u'9,1,3'
invalid_line_record = u'1,2,wibble,32.56,"bob,fred",100,"alpha,beta"'

header_batch = u'_type,_line,first,second,third,fourth,fifth\n1,1,wibble,32.56,"bob,fred",100,"alpha,beta"'

class testSingle( unittest.TestCase ):
    def test_parse( self ):
        obj = record_batch( single_record = record_format )
        output = obj.parse( raw_record )
        self.assertEqual( output, [ parsed_record ] )

    def test_parse_missing( self ):
        obj = record_batch( single_record = record_format )
        self.assertRaises(
            ParseException,
            obj.parse, invalid_record
        )

    def test_parse_missing( self ):
        obj = record_batch( single_record = record_format )
        self.assertRaises(
            ParseException,
            obj.parse, invalid_line_record
        )

    def test_unparse( self ):
        obj = record_batch( single_record = record_format )
        output = obj.unparse( [ parsed_record, ] )
        self.assertEqual( output, raw_record )

    def test_unparse_missing( self ):
        obj = record_batch( single_record = record_format )
        missing = dict( parsed_record )
        del missing[ u'second' ]
        self.assertRaises(
            ParseException,
            obj.unparse, [ missing, ]
        )

    def test_unparse_with_header( self ):
        obj = record_batch( single_record = record_format, header = True )
        output = obj.unparse( [ parsed_record, ] )
        self.assertEqual( output, header_batch )

if __name__ == u'__main__':
    unittest.main()
