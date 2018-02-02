from typing import Any
from os import path
from intermake import Theme, MCMD
from mhelper import ByRef


class StdOutWriter:
    """
    Handles writing to STDOUT instead of a file.
    """
    
    
    def __init__( self, title ) -> None:
        self.title = title
        self.lines = []
    
    
    def write( self, text ) -> None:
        self.lines.append( text )
    
    
    def close( self ) -> None:
        MCMD.print( "Writing output to STDOUT." )
        
        print( Theme.TITLE + self.title + Theme.RESET )
        
        for line in self.lines:
            print( Theme.VALUE + line + Theme.RESET, end = "" )


class NowhereWriter:
    """
    Handles writing to nothing instead of a file.
    """
    
    
    def __init__( self ) -> None:
        pass
    
    
    def write( self, text ) -> None:
        pass
    
    
    def close( self ) -> None:
        pass

def open_write( file_name, title, overwrite_all: ByRef[bool] ) -> Any:
    """
    Opens a file for writing, also accepts `stdout` as the file name.
    """
    if file_name.lower() == "stdout":
        MCMD.print( "Ready to write to standard output." )
        return StdOutWriter( title )
    elif file_name.lower() == "stdout":
        MCMD.print( "Ready to write to local data." )
        return NowhereWriter()
    else:
        MCMD.print( "Ready to write to «{}»".format( file_name ) )
        
        if path.isfile( file_name ):
            if not overwrite_all.value:
                q = MCMD.question( "The previous file «{}» is in the way and will be overwritten.".format( file_name ), [True, False, "always"] )
                
                if q is False:
                    raise FileExistsError( "A previous file «{}» is in the way.".format( file_name ) )
                elif q is True:
                    pass
                elif q == "always":
                    overwrite_all.value = True
            
            MCMD.warning( "The previous file «{}» is in the way and will be overwritten.".format( file_name ) )
        
        return open( file_name, "w" )
    