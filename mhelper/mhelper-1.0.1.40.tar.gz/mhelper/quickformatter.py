from mhelper import ansi


class QfState:
    def __init__( self, formatter ):
        assert isinstance( formatter, QuickFormatter )
        
        self.formatter = formatter
        
        self.stack = []
        self.r = []
    
    
    def format( self, text: str ):
        l = len( text )
        i = 0
        li = 0
        
        while i < l:
            c = text[i]
            
            if c == "<":
                if li != i:
                    self.append( text[li:i] )
                
                j = i + 1
                while text[j] != ">" and j < l:
                    j += 1
                
                self.append( self.process( text[i + 1:j] ) )
                i = j + 1
                li = i
            else:
                i += 1
        
        if li != i:
            self.append( text[li:i] )
        
        return "".join( r )
    
    
    def process( self, p ):
        if p == "br" or p == "br/":
            return "\n"
        elif p.startswith( "/" ):
            self.pop()
        elif p == "h1":
            self.append()
            self.push( ansi.FORE_BRIGHT_WHITE + ansi.BACK_BLUE,  )
        elif p == "h2":
            self.push( ansi.FORE_BRIGHT_WHITE + ansi.BACK_BLUE )
            
        return "*" + p + "*"
    
    
    def append( self, param ):
        self.r.append( param )
    
    
    def push( self, fg ):
        self.stack.append( fg )
        self.append( fg )
    
    
    def pop( self ):
        self.append( self.stack.pop() )


class QuickFormatter:
    def __init__( self ):
        pass
    
    
    def format( self, text: str ):
        return QfState( self ).format( text )


STANDARD = QuickFormatter()

print( "[" + STANDARD.format( "hello <world> oh world" ) + "]" )
