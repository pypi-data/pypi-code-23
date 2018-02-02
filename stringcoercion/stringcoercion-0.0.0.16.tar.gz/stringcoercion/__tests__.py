import unittest
from typing import Union, Optional, List

from stringcoercion.coercion import get_default_coercer


class MyTestCase( unittest.TestCase ):
    def __test( self, c, type_, text, expected ) -> None:
        v = c.coerce( type_, text )
        
        if v != expected:
            self.fail( "value invalid, expected {} but got {}".format(expected, v) )
            
        if not type( v ) is type( expected ):
            self.fail( "type invalid, expected {} but got {}".format(type(expected), type(v)) )
        
        
    
    
    def test_one( self ) -> None:
        c = get_default_coercer()
        
        self.__test( c, List[ bool ], "True,1,Yes,False,0,No", [ True, True, True, False, False, False ] )
        self.__test( c, Optional[ bool ], "--", None )
        self.__test( c, int, "1", 1 )
        self.__test( c, Union[ int, float ], "1", 1 )
        self.__test( c, Union[ int, float ], "1.0", 1.0 )
        self.__test( c, Union[ float, int ], "1", 1.0 )
        self.__test( c, Union[ None, bool ], "1", True )
        self.__test( c, Union[ None, bool ], "--", None )
        self.__test( c, Optional[ bool ], "True", True )
        self.__test( c, Union[ bool, str ], "beans", "beans" )
        self.__test( c, Union[ bool, str ], "yes", True )
        self.__test( c, List[ Union[ bool, str ] ], "True,1,Yes,False,0,No,Beans", [ True, True, True, False, False, False, "Beans" ] )


if __name__ == '__main__':
    unittest.main()
