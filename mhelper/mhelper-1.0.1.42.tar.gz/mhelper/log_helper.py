from typing import Union, List

import sys

from mhelper import string_helper, ansi
from mhelper.reflection_helper import TTristate


class DefaultLogger:
    def __init__( self ):
        self.print = self.__print_stderr
    
    
    def __print_stderr( self, text ):
        print( text, file = sys.stderr )


DEFAULT_LOGGER = DefaultLogger()


class Logger:
    """
    Logging simplified.
    """
    
    
    def __init__( self, name: Union[str, bool], enabled: bool = False ):
        """
        CONSTRUCTOR
        :param name:        Name of the logger 
        :param enabled:     A value for :property:`target` 
        """
        LOGGERS.append( self )
        self.name = name
        
        if name:
            self.__prefix = name + ": "
        else:
            self.__prefix = ""
        
        self.__target = None
        self.__enabled: TTristate = None
        self.target = enabled
        self.__skip = set()
    
    
    def pause( self, message = "PAUSED", *args, key = None ):
        if not self.__enabled:
            return
        
        if key and key in self.__skip:
            return
        
        message = self.format( message, *args )
        
        c = ansi.FORE_BRIGHT_WHITE + ansi.BACK_BLUE
        r = ansi.RESET
        
        if key is None:
            print( message + " " + c + "[C|D]" + r, end = "" )
        else:
            print( message + " " + c + "[C|I|D]" + r, end = "" )
        
        i = input()
        
        if i == "i" and key:
            self.__skip.add( key )
        elif i == "d":
            self.target = None
    
    
    @property
    def target( self ):
        """
        Gets or sets the target printer, which should accept one unnamed `str` parameter.
        The following are also accepted:
            `None` or `False`:  Disables printing
            `True`:             Prints to std-err.
        :return: 
        """
        return self.__target
    
    
    @property
    def enabled( self ) -> TTristate:
        return self.__enabled
    
    
    @target.setter
    def target( self, enabled: bool = None ):
        if enabled is True:
            self.__enabled = True
            self.__target = DEFAULT_LOGGER.print
        elif enabled is False or enabled is None:
            self.__enabled = False
            self.__target = None
        else:
            self.__enabled = None
            self.__target = enabled
    
    
    def __call__( self, *args ):
        if self.__target is None:
            return self
        
        self.print( self.format( *args ) )
        
        return self
    
    
    def format( self, *args ):
        if len( args ) == 1:
            return args[0]
        elif len( args ) > 1:
            vals = list( args[1:] )
            for i in range( len( vals ) ):
                v = vals[i]
                
                if type( v ) in (set, list, tuple, frozenset):
                    vals[i] = string_helper.format_array( v )
                
                vals[i] = "«" + str( vals[i] ) + "»"
            
            return args[0].format( *vals )
    
    
    def print( self, message ):
        if "\n" in message:
            for i, split in enumerate( message.split( "\n" ) ):
                self.print( ("\b\b: " if i != 0 else "") + split )
            
            return
        
        self.__target( ansi.DIM + self.__prefix + ansi.RESET + string_helper.highlight_quotes( message, "«", "»", ansi.FORE_YELLOW, ansi.RESET ) )
    
    
    def indent( self ):
        self.__prefix += "    "
        
        if len( self.__prefix ) > 100:
            from mhelper.exception_helper import ImplementationError
            raise ImplementationError( "Log indent too far." )
    
    
    def unindent( self ):
        self.__prefix = self.__prefix[:len( self.__prefix ) - 4]
    
    
    def __enter__( self ):
        self.indent()
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        self.unindent()


LOGGERS: List[Logger] = []
"""List of all loggers"""
