import os
import unittest
from datetime import datetime
from decimal import Decimal

from .. import (
    int_field,
    decimal_field,
    string_field,
    date_field,
    excel_batch,
    ParseException,
)

columns = (
    ( u'a', string_field(), ),
    ( u'b', int_field(), ),
    ( u'c', decimal_field(), ),
    ( u'd', date_field( fmt = u'%Y/%m/%d %H:%M:%S' ), ),
)

plain = (
    ( u'string', u'1', u'1.234', u'1900/01/01 00:00:00' ),
    ( u'second string', u'0', u'0.987', u'1900/01/01 00:00:00' ),
)
plain_parsed = [
    { u'a': u'string', u'b': u'1', u'c': u'1.234', u'd': u'1900/01/01 00:00:00', },
    { u'a': u'second string', u'b': u'0', u'c': u'0.987', u'd': u'1900/01/01 00:00:00', },
]

typed = (
    ( u'string', 1, Decimal( u'1.234' ), datetime( 1900, 1, 1, 0, 0, 0 ), ),
    ( u'second string', 0, Decimal( u'0.987' ), datetime( 1900, 1, 1, 0, 0, 0 ), ),
)
typed_parsed = [
    {
        u'a': u'string',
        u'b': 1,
        u'c': Decimal( u'1.234' ),
        u'd': datetime( 1900, 1, 1, 0, 0, 0 ),
    },
    {
        u'a': u'second string',
        u'b': 0,
        u'c': Decimal( u'0.987' ),
        u'd': datetime( 1900, 1, 1, 0, 0, 0 ),
    },
]

short = (
    ( u'string', 1, Decimal( u'1.234' ), datetime( 1900, 1, 1, 0, 0, 0 ), ),
    ( u'second string', 0, Decimal( u'0.987' ), ),
)

class testExcel( unittest.TestCase ):

    def setUp( self ):
        loc = os.path.dirname( __file__ )
        self.fname = os.path.join( loc, u'types.xlsx' )

    def test_parse_types( self ):
        obj = excel_batch( columns = columns )
        with open( self.fname, 'rb' ) as inf:
            fdata = inf.read()
        pdata = obj.parse( fdata )
        self.assertEqual( pdata, typed_parsed )

    def test_unparse_with_columns( self ):
        obj = excel_batch( columns = columns )
        pdata = obj.unparse( typed )
        odata = obj.parse( pdata )
        self.assertEqual( odata, typed_parsed )

    def test_unparse_with_header_success( self ):
        obj = excel_batch( columns = columns, header = True )
        pdata = obj.unparse( typed_parsed )
        odata = obj.parse( pdata )
        self.assertEqual( odata, typed_parsed )

    def test_unparse_with_property( self ):
        obj = excel_batch( columns = columns, header = True )
        pdata = obj.unparse( typed_parsed, properties = { u'creator': u'bob' } )
        odata = obj.parse( pdata )
        self.assertEqual( odata, typed_parsed )

    def test_unparse_fail( self ):
        obj = excel_batch( columns = columns )
        self.assertRaises(
            ParseException,
            obj.unparse, short
        )

if __name__ == u'__main__':
    unittest.main()
