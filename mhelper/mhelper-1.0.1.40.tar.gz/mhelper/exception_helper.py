import subprocess
import traceback
from typing import Iterable, Union, Optional

import itertools


TType = Union[type, Iterable[type]]
"""A type, or a collection of types"""


class NotSupportedError( Exception ):
    """
    Since `NotImplementedError` looks like an abstract-base-class error to the IDE, `NotSupportedError` provides a more explicit alternative.
    """
    pass


class LogicError( Exception ):
    """
    Signifies a logical error in the subroutine which generally isn't the caller's fault.
    """
    pass


ImplementationError = LogicError
"""Alias for LogicError"""


class NotFoundError( Exception ):
    """
    Like FileNotFound error, but when applied to something other than files.
    """
    pass


class SwitchError( Exception ):
    """
    An error selecting the case of a switch.
    """
    
    
    def __init__( self, name: str, value: object, *, instance: bool = False, details: Optional[str] = None ):
        """
        CONSTRUCTOR
        
        :param name:        Name of the switch 
        :param value:       Value passed to the switch 
        :param instance:    Set to indicate the switch is on the type of value (`type(value)`)
        :param details:     Additional message to append to the error text. 
        """
        if details is not None:
            details = " Further details: {}".format( details )
        
        if instance:
            super().__init__( "The switch on the type of «{}» does not recognise the value «{}» of type «{}».{}".format( name, value, type( value ), details ) )
        else:
            super().__init__( "The switch on «{}» does not recognise the value «{}» of type «{}».{}".format( name, value, type( value ), details ) )


class SubprocessError( Exception ):
    """
    Raised when the result of calling a subprocess indicates an error.
    """
    pass


def add_details( exception: Exception, **kwargs ) -> None:
    """
    Attaches arbitrary information to an exception.
    
    :param exception:   Exception 
    :param kwargs:      Information to attach
    """
    args = list( exception.args )
    
    message = create_details_message( **kwargs )
    
    if len( args ) > 0 and isinstance( args[0], str ):
        args[0] += message
    else:
        args.append( message )
    
    exception.args = tuple( args )


def create_details_message( **kwargs ):
    from mhelper import string_helper
    
    result = [""]
    
    lk = 1
    lt = 1
    
    for k, v in kwargs.items():
        lk = max( len( str( k ) ), lk )
        lt = max( len( string_helper.type_name( v ) ), lt )
    
    for k, v in kwargs.items():
        result.append( "--> {0} ({1}) = «{2}»".format( str( k ).ljust( lk ), string_helper.type_name( v ).ljust( lt ), v ) )
    
    return "\n".join( result )


def assert_type( name, value, type ):
    if not isinstance( value, type ):
        from mhelper.string_helper import type_name
        raise TypeError( "`{0}` should be of type `{1}`, but it is a `{2}` with value `{3}`.".format( name, type.__name__, type_name( value ), value ) )


def exception_to_string( ex: BaseException ):
    result = []
    
    while ex:
        result.append( str( ex ) )
        ex = ex.__cause__
    
    return "\n---CAUSED BY---\n".join( result )


def run_subprocess( command: str ) -> None:
    """
    Runs a subprocess, raising `SubprocessError` if the error code is set.
    """
    status = subprocess.call( command, shell = True )
    
    if status:
        raise SubprocessError( "The command «{}» exited with error code «{}». If available, checking the console output may provide more details.".format( command, status ) )


def format_types( type_: TType ) -> str:
    if isinstance( type_, type ):
        return str( type_ )
    else:
        from mhelper import string_helper
        return string_helper.join_ex( type_, delimiter = ", ", last_delimiter = " or ", formatter = "«{}»" )


def assert_instance( name: str, value: object, type_: TType ):
    if isinstance( type_, type ):
        type_ = (type_,)
    
    if not any( isinstance( value, x ) for x in type_ ):
        raise TypeError( instance_message( name, value, type_ ) )


def assert_instance_or_none( name: str, value: object, type_: type ):
    if isinstance( type_, type ):
        type_ = (type_,)
    
    type_ = list( itertools.chain( type_, (type( None ),) ) )
    
    assert_type( name, value, type_ )


def instance_message( name: str, value: object, type_: TType ) -> str:
    """
    Creates a suitable message describing a type error.
    :param name:        Name 
    :param value:       Value 
    :param type_:       Expected type 
    :return:            The message
    """
    return "The value of «{}», which is «{}», should be of type {}, but it's not, it's a «{}».".format( name, value, format_types( type_ ), type( value ) )


def full_traceback():
    return "**** Handler Traceback ****\n" + current_stack_text() + "\n**** Error traceback ****\n" + traceback.format_exc()


def current_stack_text():
    return "\n".join( x.strip() for x in traceback.format_stack() )


def type_error( name: str, value: object, type_: TType ) -> None:
    """
    Raises a `TypeError` with an appropriate message.
    
    :param name:        Name 
    :param value:       Value 
    :param type_:       Expected type 
    :except:            TypeError
    """
    raise TypeError( instance_message( name, value, type_ ) )
