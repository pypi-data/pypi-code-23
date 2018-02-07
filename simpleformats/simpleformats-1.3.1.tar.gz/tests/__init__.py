import unittest

from .testfield import (
    testIntField,
    testDecimalField,
    testBooleanField,
    testStringField,
    testStringMatches,
    testDateField,
    testConstantField,
    testFieldObject,
)
from .testrecord import testDelimited,testFixedWidth
from .testsinglebatch import testSingle
from .testmultibatch import testMulti
from .testjsonbatch import testJSON
from .testxmlbatch import testXML
from .testexcelbatch import testExcel

def suite():
    test_suite = unittest.TestSuite()

    test_suite.addTest( unittest.makeSuite(testIntField) )
    test_suite.addTest( unittest.makeSuite(testDecimalField) )
    test_suite.addTest( unittest.makeSuite(testBooleanField) )
    test_suite.addTest( unittest.makeSuite(testStringField) )
    test_suite.addTest( unittest.makeSuite(testStringMatches) )
    test_suite.addTest( unittest.makeSuite(testDateField) )
    test_suite.addTest( unittest.makeSuite(testConstantField) )
    test_suite.addTest( unittest.makeSuite(testFieldObject) )

    test_suite.addTest( unittest.makeSuite(testDelimited) )
    test_suite.addTest( unittest.makeSuite(testFixedWidth) )

    test_suite.addTest( unittest.makeSuite(testSingle) )
    test_suite.addTest( unittest.makeSuite(testMulti) )
    test_suite.addTest( unittest.makeSuite(testJSON) )
    test_suite.addTest( unittest.makeSuite(testXML) )
    test_suite.addTest( unittest.makeSuite(testExcel) )

    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run( suite() )
