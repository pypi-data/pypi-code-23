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

untyped_values = [ u'wibble', u'32.56', u'bob,fred', u'100', u'alpha,beta' ]

header_data = {
    u'_type': 0,
    u'sequence': 1,
}
type1_data = {
    u'_type': 1,
    u'first': u'wibble',
    u'second': Decimal( '32.56' ),
    u'third': u'bob,fred',
    u'fourth': 100,
    u'fifth': u'alpha,beta',
}
error1_data = {
    u'_type': 5,
    u'blah': u'blahblah',
}
error2_data = {
    u'wrong': u'so wrong',
}
error3_data = {
    u'_type': 1,
    u'first': u'wibble',
    u'second': u'uhoh',
    u'third': u'bob,fred',
    u'fourth': 100,
    u'fifth': u'alpha,beta',
}
footer_data = {
    u'_type': 9,
}

header = delimited_record(
    ( u'_type', int_field() ),
    ( u'sequence', int_field() ),
)
type1 = delimited_record(
    ( u'_type', int_field() ),
    ( u'first', string_field() ),
    ( u'second', decimal_field() ),
    ( u'third', string_field() ),
    ( u'fourth', int_field() ),
    ( u'fifth', string_field() ),
)
footer = delimited_record(
    ( u'_type', int_field() ),
    ( u'_line', int_field() ),
)

header_record = u'0,1'
type1_record = u'1,wibble,32.56,"bob,fred",100,"alpha,beta"'
footer_record = u'9,3'
batch = u'{}\n{}\n{}'.format( header_record, type1_record, footer_record )
line_error_batch = u'{}\n{}\n9,4'.format( header_record, type1_record )
type_error_batch = u'{}\n{}\n8,3'.format( header_record, type1_record )

class testMulti( unittest.TestCase ):

    def test_parse( self ):
        obj = record_batch( multi_record = { 0: header, 1: type1, 9: footer } )
        output = obj.parse( batch )

        # line number is auto-added, so put it in here for comparison
        actual_footer = dict( footer_data )
        actual_footer.update( { u'_line': 3 } )

        self.assertEqual( len(output), 3 )
        self.assertEqual( output[0], header_data )
        self.assertEqual( output[1], type1_data )
        self.assertEqual( output[2], actual_footer )

    def test_parse_invalid_line( self ):
        obj = record_batch( multi_record = { 0: header, 1: type1, 9: footer } )
        self.assertRaises(
            ParseException,
            obj.parse, line_error_batch
        )

    def test_parse_invalid_type( self ):
        obj = record_batch( multi_record = { 0: header, 1: type1, 9: footer } )
        self.assertRaises(
            ParseException,
            obj.parse, type_error_batch
        )

    def test_unparse( self ):
        obj = record_batch( multi_record = { 0: header, 1: type1, 9: footer } )
        output = obj.unparse( [ header_data, type1_data, footer_data ] )
        self.assertEqual( output, batch )

    def test_unparse_invalid_record_type( self ):
        obj = record_batch( multi_record = { 0: header, 1: type1, 9: footer } )
        self.assertRaises(
            ParseException,
            obj.unparse, [ header_data, error1_data, footer_data ]
        )

    def test_unparse_missing_type( self ):
        obj = record_batch( multi_record = { 0: header, 1: type1, 9: footer } )
        self.assertRaises(
            ParseException,
            obj.unparse, [ header_data, error2_data, footer_data ]
        )

    def test_unparse_invalid_record_data( self ):
        obj = record_batch( multi_record = { 0: header, 1: type1, 9: footer } )
        self.assertRaises(
            ParseException,
            obj.unparse, [ header_data, error3_data, footer_data ]
        )

    def test_unparse_header_error( self ):
        obj = record_batch(
            multi_record = { 0: header, 1: type1, 9: footer },
            header = True,
        )
        self.assertRaises(
            ParseException,
            obj.unparse, [ header_data, error2_data, footer_data ]
        )
        

if __name__ == u'__main__':
    unittest.main()
