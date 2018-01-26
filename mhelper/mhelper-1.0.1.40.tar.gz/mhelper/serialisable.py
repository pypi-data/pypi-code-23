from typing import Tuple, Iterable


class Serialisable:
    """
    Provides overridable methods for dealing with serialisation easier.
    
        ```
        _SERIALISABLE_state
        ``` 
        
    Unlike `__getstate__` __setstate__`:
        * The state only needs to be specified once.
        * The non-serialised fields are specified rather than the serialisable ones.
    """
    
    
    def _SERIALISABLE_state( self ) -> Iterable[Tuple[type, str, object]]:
        """
        Gets the serialisation state.
        
        :return: The derived class should return (typically through a sequence of `yield` statements)
                 an iterable over tuples describing the non-serialisable objects.
            Iterable:
                Tuple:
                    type:   The type of the class on which the field is present
                    str:    The name of the field
                    object: The default value of the field when the object is deserialized
        """
        return []
    
    
    def __get_state( self, test ):
        d = { }
        
        for class_, field, value in self._SERIALISABLE_state():
            if field.startswith( "__" ) and not field.endswith( "__" ):
                field = "_{}{}".format( class_.__name__, field )
            
            if test and field not in self.__dict__:
                raise ValueError( "No such field as `{}`.".format( field ) )
            
            d[field] = value
        
        return d
    
    
    def __getstate__( self ):
        result = dict( self.__dict__ )
        
        for x in self.__get_state( True ).keys():
            del result[x]
        
        return result
    
    
    def __setstate__( self, state ):
        for k, v in state.items():
            setattr( self, k, v )
        
        for k, v in self.__get_state( False ).items():
            setattr( self, k, v )
