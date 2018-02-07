from decimal import Decimal
import unittest

from .. import (
    int_field,
    decimal_field,
    string_field,
    date_field,
    xml_batch,
    ParseException,
)

test_format = {
    u'one': {
        u'@property': string_field( required = False ),
        u'two': [ { u'three': decimal_field(), } ],
    },
}

valid_xml = u'<one><two><three>9.3</three></two><two><three>1.2</three></two></one>'

valid_parsed = {
    u'one': {
        u'@property': '',
        u'two': [
            { u'three': Decimal( '9.3' ) }, { u'three': Decimal( '1.2' ) }
        ]
    }
}
invalid_one = {
    u'one': {
    },
    u'two': [
        { u'three': Decimal( '9.3' ) }, { u'three': Decimal( '1.2' ) }
    ]
}
invalid_two = {
    u'one': {
        u'two': [ { u'four': Decimal( '9.3' ) }, { u'four': Decimal( '1.2' ) } ],
    },
}

class testXML( unittest.TestCase ):

    def test_parse_with_format( self ):
        obj = xml_batch( format = test_format )
        result = obj.parse( valid_xml )
        self.assertEqual( result, valid_parsed )

    # http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    # defines these test cases
    def test_unparse_xml_com( self ):
        obj = xml_batch()
        self.assertEqual( obj.unparse( { u'e': None } ), u'<e />' )
        self.assertEqual( obj.unparse( { u'e': u'text' } ), u'<e>text</e>' )
        self.assertEqual(
            obj.unparse( { u'e': { u'@name': u'value' } } ),
            u'<e name="value" />'
        )
        self.assertEqual(
            obj.unparse( { u'e': { u'@name': u'value', u'#text': u'text' } } ),
            u'<e name="value">text</e>'
        )
        self.assertEqual(
            obj.unparse( { u'e': { u'a': u'text', u'b': u'text' } } ),
            u'<e><a>text</a><b>text</b></e>'
        )
        self.assertEqual(
            obj.unparse( { u'e': { u'a': [ u'text', u'text' ] } } ),
            u'<e><a>text</a><a>text</a></e>',
        )
        self.assertEqual(
            obj.unparse( { u'e': { u'#text': u'text', u'a': u'text' } } ),
            u'<e>text<a>text</a></e>',
        )

    def test_unparse_fail_one( self ):
        obj = xml_batch( format = test_format )
        self.assertRaises(
            ParseException,
            obj.unparse, invalid_one
        )

    def test_unparse_fail_two( self ):
        obj = xml_batch( format = test_format )
        self.assertRaises(
            ParseException,
            obj.unparse, invalid_two
        )

if __name__ == u'__main__':
    unittest.main()
