"""
Defines the `@itemproperty` decorator and its supporting classes.
"""


def itemproperty( f ):
    """
    Like the `@property` decorator, but creates an indexable property.
    
    Note that the _setter_ is called `itemsetter` and not `setter`.
    (This is to avoid PyLint or IDEs being confused as they make certain assumptions about `.setter` decorators.)
    
    ```
    class MyClass:
        @itemproperty
        def eggs( item ):
            return self._eggs[item]
            
        @eggs.itemsetter
        def eggs( item, value ):
           self._eggs[item] = value 
    
    m = MyClass()
    m.eggs["spam"] = "beans"
    print( m.eggs["spam"] )
    ``` 
    """
    return _ItemPropertyClass( f )


class _ItemPropertyClass:
    def __init__( self, getter ):
        self._getter = getter
        self._setter = None
    
    
    def __get__( self, instance, owner ):
        return _BoundItemPropertyClass( instance, self )
    
    
    def itemsetter( self, setter ):
        self._setter = setter
        return self


class _BoundItemPropertyClass:
    def __init__( self, self2, class_: _ItemPropertyClass ):
        self.__self2 = self2
        self.__class = class_
    
    
    def __getitem__( self, item ):
        return self.__class._getter( self.__self2, item )
    
    
    def __setitem__( self, key, value ):
        return self.__class._setter( self.__self2, key, value )
