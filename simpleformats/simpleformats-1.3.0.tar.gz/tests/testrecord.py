from decimal import Decimal
import unittest

from .. import (
    int_field,
    decimal_field,
    string_field,
    date_field,
    ParseException
)

from ..record import (
    parse_delimited_record,
    unparse_delimited_record,
    delimited_record,
    fixedwidth_record,
)

data = {
    u'first': u'wibble',
    u'second': Decimal( u'32.56' ),
    u'third': u'bob,fred',
    u'fourth': 100,
    u'fifth': u'alpha,beta',
}
data_header = u'first,second,third,fourth,fifth'
untyped_values = [ u'wibble', u'32.56', u'bob,fred', u'100', u'alpha,beta' ]

delimited_args = (
    ( u'first', string_field() ),
    ( u'second', decimal_field() ),
    ( u'third', string_field() ),
    ( u'fourth', int_field() ),
    ( u'fifth', string_field() ),
)

fixedwidth_args = (
    ( u'first', string_field( 0, 10 ) ),
    ( u'second', decimal_field( 10, 17, filler = ' ' ) ),
    ( u'third', string_field( 17, 32 ) ),
    ( u'fourth', int_field( 32, 37 ) ),
    ( u'fifth', string_field( 37, 47 ) ),
)

delimitedrecord = u'"wibble",32.56,"bob,fred",100,"alpha,beta"'
unparsedrecord = u'wibble,32.56,"bob,fred",100,"alpha,beta"'
fixedwidthrecord = u'    wibble  32.56       bob,fred00100alpha,beta'

class testDelimited( unittest.TestCase ):
    def test_parse_record_valid( self ):
        output = parse_delimited_record( delimitedrecord[0:14] )
        self.assertEqual( output, untyped_values[0:2] )

    def test_parse_quoted_delimiter( self ):
        output = parse_delimited_record( delimitedrecord[0:25] )
        self.assertEqual( output, untyped_values[0:3] )

    def test_parse_quotes_at_end( self ):
        output = parse_delimited_record( delimitedrecord )
        self.assertEqual( output, untyped_values )

    def test_parse_unfinished_quotes( self ):
        self.assertRaises(
            ParseException,
            parse_delimited_record, delimitedrecord[0:24]
        )

    def test_unparse_record_valid( self ):
        output = unparse_delimited_record( untyped_values )
        self.assertEqual( output, unparsedrecord )

    def test_delimited_class_parse_valid( self ):
        obj = delimited_record( *delimited_args )
        output = obj.parse( delimitedrecord )
        self.assertEqual( output, data )

    def test_delimited_class_parse_invalid( self ):
        obj = delimited_record( *delimited_args )
        self.assertRaises(
            ParseException,
            obj.parse, delimitedrecord[0:14]
        )

    def test_delimited_class_unparse_valid( self ):
        obj = delimited_record( *delimited_args )
        output = obj.unparse( data )
        self.assertEqual( output, unparsedrecord )

    def test_delimited_class_unparse_invalid( self ):
        obj = delimited_record( *delimited_args )
        missing = dict( data )
        del missing[ u'third' ]
        self.assertRaises(
            ParseException,
            obj.unparse, missing
        )

    def test_delimited_class_as_header( self ):
        obj = delimited_record( *delimited_args )
        output = obj.as_header()
        self.assertEqual( output, data_header )

class testFixedWidth( unittest.TestCase ):
    def test_fixedwidth_record_parse( self ):
        obj = fixedwidth_record( *fixedwidth_args )
        output = obj.parse( fixedwidthrecord )
        self.assertEqual( output, data )

    def test_fixedwith_record_unparse_valid( self ):
        obj = fixedwidth_record( *fixedwidth_args )
        output = obj.unparse( data )
        self.assertEqual( output, fixedwidthrecord )

    def test_fixedwith_record_unparse_invalid( self ):
        obj = fixedwidth_record( *fixedwidth_args )
        missing = dict( data )
        del missing[ u'third' ]
        self.assertRaises(
            ParseException,
            obj.unparse, missing
        )

if __name__ == u'__main__':
    unittest.main()
