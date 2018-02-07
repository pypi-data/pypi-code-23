import time
import unittest
from datetime import datetime
from decimal import Decimal

from .. import (
    json_batch,
    ParseException,
)
from simpleformats.batch.json_batch import encodejson

class testJSON( unittest.TestCase ):

    def test_encode_decimal( self ):
        obj = encodejson()
        output = obj.default( Decimal( u'0.123' ) )
        self.assertEqual( output, u'0.123' )

    def test_encode_datetime( self ):
        obj = encodejson()
        output = obj.default( datetime( 1900, 1, 1, 0, 0, 0 ) )
        self.assertEqual( output, u'1900-01-01 00:00:00' )

    def test_encode_time_struct( self ):
        obj = encodejson()
        output = obj.default(
            time.strptime( u'1900-01-01 00:00:00', u'%Y-%m-%d %H:%M:%S' )
        )
        self.assertEqual( output, u'1900-01-01 00:00:00' )

    def test_parse_exception( self ):
        obj = json_batch()
        self.assertRaises(
            ParseException,
            obj.parse, u']f[wf['
        )

    def test_unparse_exception( self ):
        obj = json_batch()
        self.assertRaises(
            ParseException,
            obj.unparse, obj
        )

if __name__ == u'__main__':
    unittest.main()
