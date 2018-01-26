from typing import Optional, Callable


class ManagedWith:
    """
    Wraps a (presumably pooled) object.
    
    Usage:

        ```
        with ManagedWith(...):
            ...
        ```
        
    Example (database provider):
    
        def get_database():
            return ManagedWith(pool.pop(), pool.push)
        
    Example (from `Plugin`):
        
        ```
        with get_database() as db:
            db.execute("RETURN 1")
        ```
    """
    
    
    def YOURE_USING_THE_WRONG_THING( self ):
        """
        Message to an IDE user telling them they're using the wrong thing! (should be using `with`)
        """
        pass
    
    
    def __init__( self,
                  target: Optional[ object ] = None,
                  on_exit: Callable[[Optional[ object]], None] = None,
                  on_enter: Callable[[Optional[ object]], None] = None,
                  on_get_target: Callable[[ ], object] = None ):
        """
        :param target: Object to manage 
        :param on_exit: What to do when the caller has finished with the target 
        """
        self.__target = target
        self.__on_exit = on_exit
        self.__on_enter = on_enter
        self.__on_get_target = on_get_target
        
        if self.__on_get_target is not None and self.__target is not None:
            raise ValueError( "Cannot specify both 'on_get_target' and 'target' parameters." )
    
    
    def __enter__( self ):
        if self.__on_get_target is not None:
            self.__target = self.__on_get_target()
        
        if self.__on_enter is not None:
            self.__on_enter( self.__target )
        
        return self.__target
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        if self.__on_exit is not None:
            self.__on_exit( self.__target )
        
        if self.__on_get_target is not None:
            self.__target = None
