"""
Module for dealing with coercing values to strings.
See `readme.md` in the project root for details.
"""

from enum import Enum
from traceback import format_exc
from typing import List, Optional, Sequence, Tuple, Type, cast

from mhelper import AnnotationInspector, Password, array_helper, ignore, string_helper


class CoercionInfo:
    """
    :data collection:           Calling coercer collection
    :data annotation:           An `AnnotationInspector`, providing information on the intended format to coerce into.
    :data source:               Value to translate from. Undefined during queries inside the `can_handle` function.
    :data cancel:               Setting this to `True` prevents further `Coercer`s trying to covert this value to this annotation (other annotations may still proceed).
    """
    
    
    def __init__( self, annotation: object, collection: "CoercerCollection", source: Optional[str] ):
        """
        CONSTRUCTOR
        See class comments for parameters.
        """
        self.collection = collection
        self.annotation = AnnotationInspector( annotation )
        self.source = source
        self.cancel = False
    
    
    def __str__( self ):
        return "Coerce «{}» into {}".format( self.source, self.annotation )


class CoercionError( Exception ):
    """
    Raised when an individual Coercer fails, and also when all coercers have failed.
    """
    pass


class Coercer:
    """
    Coercer base class.
    """
    
    
    class PRIORITY:
        """
        Priorities namespace.
        
        :data _NONE:       Coercer is unused. Equivalent to `None` and `False`.
        :data _HIGHEST:    Highest valid priority (lowest value).
        :data _LOWEST:     Lowest expected (highest value).
        :data HIGH:        A priority above the default
        :data DEFAULT:     The default recommended priority for user coercers. Equivalent to `True`.
        :data INBUILT:     The priority used by the inbuilt coercers, which is lower than DEFAULT.
        :data FALLBACK:    The priority used by the fallback coercer. No priority should be lower.
        """
        _NONE = 0
        _HIGHEST = 1
        HIGH = 25
        DEFAULT = 50
        INBUILT = 75
        FALLBACK = 100
        _LOWEST = 100
        
    
    def can_handle( self, info: CoercionInfo ):
        """
        ABSTRACT
        Determines if the coercer can handle this coercion.
        
        :param info:    Details on the coercion. The `source` field is indeterminate during the query and should be ignored. 
        :return: `True` (DEFAULT_PRIORITY), or an `int` above 1 denoting the priority of this coercer in relation to the others. 
        """
        raise NotImplementedError( "abstract" )
    
    
    def coerce( self, info: CoercionInfo ) -> Optional[object]:
        """
        ABSTRACT
        Performs the actual coercion.
        This will only ever be called if `can_handle` returned a non-False value previously.
        
        :param info:            Details on the coercion to perform. 
        :return:                The object in the designated type or format.
        :except CoercionError:  This error should be raised if the coercion cannot be performed. The next coercer in the queue will then be attempted.
        """
        raise NotImplementedError( "abstract" )
    
    
    def __str__( self ):
        return type( self ).__name__


class CoercerCollection:
    """
    Collection of coercers.
    
    Use `register` to register the coercers and `coerce` to coerce strings to values.
    
    See also `get_default_coercer`.
    
    :data coercers: The collection
    :data debug:    Set this to true to print status messages from each coercion by default.
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        self.coercers = []  # List[Coercer]
        self.__debug_depth = 0
        self.debug = False
    
    
    def register( self, *args: Coercer ):
        """
        Registers a new coercer or coercers.
        
        :param args:    Coercer(s) to register
        """
        for arg in args:
            self.coercers.append( arg )
    
    
    def __str__( self ):
        return "CoercerCollection with «{}» registered coercers: {}.".format( len( self.coercers ), ", ".join( "«{}»".format( x ) for x in self.coercers ) )
    
    
    def coerce( self, types: object, value: str ):
        """
        Tries all registered coercers to coerce the string into the specified type(s).
        
        :param types:           An acceptable type, sequence of types, annotation, or sequence of annotations.
                                (annotations can be any arbitrary objects that at least one registered Coercer is
                                 able to understand, e.g. `Union`. They do not need to be derived from `type`.)
                                If a sequence is provided, the elements will be tried in order, for each coercer in turn.
                                The exact types and/or annotations accepted depend on which coercers you have registered.
                                 
        :param value:           Source text to coerce.
                                If this starts with `"coerce::"` then debugging information is printed.
                                
        :return:                Source text converted to as one of the types in `types`
        
        :except CoercionError:  Coercion failed. 
        """
        orig_debug = None
        
        if value.startswith( "coerce::" ):
            value = value[len( "coerce::" ):]
            orig_debug = self.debug
            self.debug = True
        
        types: Sequence[type] = array_helper.as_sequence( types )
        multiple_types: bool = len( types ) != 1
        
        handlers = []
        
        self.__debug_depth += 1
        prefix = "::::" * self.__debug_depth
        
        if self.debug:
            type_str = " | ".join( "«{}»".format( x ) for x in types )
            
            if self.__debug_depth == 1:
                print( "===== BEGIN COERCE «{}» INTO «{}» =====".format( value, type_str ) )
            else:
                print( prefix + "DESCENDING INTO «{}»".format( type_str ) )
        
        try:
            if self.debug:
                print( prefix + "ESTABLISHING PRIORITIES:" )
            
            for destination_type in cast( List[type], types ):
                coercion_info = CoercionInfo( destination_type, self, value )
                
                for coercer in self.coercers:
                    priority = coercer.can_handle( coercion_info )
                    
                    if priority is None:
                        priority = 0
                    elif priority is True:
                        priority = Coercer.PRIORITY.DEFAULT
                    elif priority is False:
                        priority = 0
                    
                    if self.debug:
                        print( prefix + " * {} --> {}".format( coercer, priority ) )
                    
                    if priority:
                        handlers.append( (priority, coercion_info, coercer) )
            
            if not handlers:
                raise CoercionError( "There isn't a handler, in «{}» handlers, that can handle «{}». Details: {}".format( len( self.coercers ), self.__get_type_names( types ), self ) )
            
            exceptions = []
            handlers = [x for x in sorted( handlers, key = lambda y: y[0] )]
            
            if self.debug:
                print( prefix + "READY TO TRY:" )
                
                for index, (priority, coercion_info, coercer) in enumerate( handlers ):
                    print( prefix + " * {}. {} --> {}".format( index, coercer, coercion_info.annotation if multiple_types else "*" ) )
                
                print( prefix + "TRYING:" )
            
            for index, (priority, coercion_info, coercer) in enumerate( handlers ):
                try:
                    if not coercion_info.cancel:
                        if self.debug:
                            print( prefix + " * {}. {} --> {}".format( index, coercer, coercion_info.annotation if multiple_types else "*" ) )
                        result = coercer.coerce( coercion_info )
                        if self.debug:
                            print( prefix + "     - SUCCESS = {} {}".format( result, type( result ) ) )
                        return result
                except Exception as ex:
                    if self.debug:
                        print( prefix + "     - FAILURE = {}\n{}".format( ex, format_exc() ) )
                    exceptions.append( (coercion_info, coercer, ex) )
            
            assert len( exceptions )
            
            self.__failure( types, value, exceptions )
        finally:
            self.__debug_depth -= 1
            
            if orig_debug is not None:
                self.debug = orig_debug
    
    
    @staticmethod
    def __get_type_names( destination_types ):
        return "|".join( str( x ) for x in destination_types )
    
    
    def __failure( self, destination_types, source_value, exceptions: List[Tuple[CoercionInfo, str, Exception]] ):
        """
        Raises a descriptive `CoercionError` to indicate coercion failure.
        """
        if not self.debug:
            raise CoercionError( "The value «{0}» is not a valid value (expected «{1}»). Use «coerce::{0}» for details.".format( source_value, self.__get_type_names( destination_types ) ) )
        
        message = []
        
        ignore( source_value )
        message.append( 'Cannot coerce into «{}».'.format( self.__get_type_names( destination_types ) ) )
        
        for index, exx in enumerate( exceptions ):
            args, coercer, ex = exx
            message.append( "  " + str( ex ).replace( "\n", "\n  " ) )
        
        # We do raise `from` because even though we've already included the description because it makes debugging easier
        raise CoercionError( "\n".join( message ) ) from exceptions[0][-1]


class UnionCoercer( Coercer ):
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if info.annotation.is_union else None
    
    
    def coerce( self, info: CoercionInfo ):
        params = info.annotation.union_args
        return info.collection.coerce( params, info.source )


class NoneTypeCoercer( Coercer ):
    def coerce( self, args: CoercionInfo ):
        if args.source == "--":
            return None
        
        raise CoercionError( "Only accepting «--» to mean «None» and «{}» is not «--».".format( args.source ) )
    
    
    def can_handle( self, info: CoercionInfo ):
        return info.annotation.value is type( None )


class EnumCoercer( Coercer ):
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.is_directly_below( Enum )) else None
    
    
    def coerce( self, args: CoercionInfo ):
        opts = [x for x in cast( Type[Enum], args.annotation.value ) if isinstance( x, args.annotation.value )]  # type: List[Enum]
        
        try:
            return string_helper.find( source = opts,
                                       search = args.source.lower(),
                                       namer = lambda x: x.name.lower(),
                                       detail = "option",
                                       fuzzy = True )
        except Exception as ex:
            args.cancel = True  # Halting now to prevent fallback to `str`.
            raise CoercionError( "«" + args.source + "» is not a valid option in: " + ", ".join( "«{}»".format( x.name ) for x in opts ) ) from ex


class BoolCoercer( Coercer ):
    def coerce( self, args: CoercionInfo ):
        try:
            return string_helper.to_bool( args.source )
        except Exception as ex:
            args.cancel = True  # Halting now to prevent fallback to True.
            raise CoercionError( "«" + args.source + "» is not a valid boolean in: «true», «false», «yes», «no», «t», «f», «y», «n», «1», «0»" ) from ex
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.value is bool) else None


class ListCoercer( Coercer ):
    def coerce( self, args: CoercionInfo ):
        # noinspection PyUnresolvedReferences
        list_type_ = args.annotation.generic_list_type
        elements = args.source.split( "," )
        result = list()
        
        for x in elements:
            result.append( args.collection.coerce( list_type_, x ) )
        
        return result
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if info.annotation.is_generic_list else None


class PasswordCoercer( Coercer ):
    def coerce( self, info: CoercionInfo ):
        if info.source in ("*", "prompt"):
            print( "Prompting for password." )
            import getpass
            value = getpass.getpass( "(PLEASE ENTER PASSWORD)" )
            
            if not value:
                raise CoercionError( "No password provided." )
            
            return info.annotation.value( value )
        else:
            return info.annotation.value( info.source )
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.is_directly_below( Password )) else None


class ObjectCoercer( Coercer ):
    def coerce( self, args: CoercionInfo ):
        return args.source
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.value is object) else None


class FallbackCoercer( Coercer ):
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.FALLBACK
    
    
    def coerce( self, args: CoercionInfo ):
        try:
            return args.annotation.value( args.source )
        except Exception as ex:
            raise CoercionError( "Cannot coerce the value via the constructor «{}».".format( args.annotation ) ) from ex


__default_coercer = None


def get_default_coercer() -> CoercerCollection:
    global __default_coercer
    
    if __default_coercer is None:
        __default_coercer = CoercerCollection()
        __default_coercer.register( PasswordCoercer() )
        __default_coercer.register( UnionCoercer() )
        __default_coercer.register( NoneTypeCoercer() )
        __default_coercer.register( EnumCoercer() )
        __default_coercer.register( BoolCoercer() )
        __default_coercer.register( ListCoercer() )
        __default_coercer.register( ObjectCoercer() )
        __default_coercer.register( FallbackCoercer() )
    
    return __default_coercer


def register( *args: Coercer ):
    return get_default_coercer().register( *args )
