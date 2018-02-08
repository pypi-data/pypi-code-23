import math

from pyparsing import CaselessLiteral, Combine, Forward, Literal, Optional, Word, ZeroOrMore, nums


class ParserFunction:
    def __init__( self, name, function, arguments, precedence = None, text = None ):
        """
        
        :param name:            Name of function 
        :param function:        Function to call 
        :param arguments:       Number of arguments 
        :param precedence:      Precedence, in range -1 to 2 inclusive, indicates the expression is a unary or binary operator. 
        """
        self.name = name
        self.function = function
        self.arguments = arguments
        self.precedence = precedence
        self.text = text
    
    
    @property
    def id( self ):
        return self.name if (self.precedence != -1 or self.arguments != 1) else "@" + self.name
    
    
    def __str__( self ):
        return "<{}{}>".format( self.text or self.id, "#" * self.arguments )


class ParserFunctions:
    def __init__( self ):
        functions = [ ]
        
        functions.append( ParserFunction( "-", lambda r: - float( r ), 1, precedence = -1, text = "NEG" ) )
        functions.append( ParserFunction( "+", lambda l, r: float( l ) + float( r ), 2, 2, text = "ADD" ) )
        functions.append( ParserFunction( "-", lambda l, r: float( l ) - float( r ), 2, 2, text = "SUB" ) )
        functions.append( ParserFunction( "*", lambda l, r: float( l ) * float( r ), 2, 2, text = "MUL" ) )
        functions.append( ParserFunction( "/", lambda l, r: float( l ) / float( r ), 2, 1, text = "DIV" ) )
        functions.append( ParserFunction( "^", lambda l, r: float( l ) ** float( r ), 2, 0, text = "POW" ) )
        functions.append( ParserFunction( "&", lambda l, r: str( l ) + str( r ), 2, 2, text = "ADD" ) )
        functions.append( ParserFunction( "SIN", lambda l: math.sin( float( l ) ), 1 ) )
        functions.append( ParserFunction( "COS", lambda l: math.cos( float( l ) ), 1 ) )
        functions.append( ParserFunction( "TAN", lambda l: math.tan( float( l ) ), 1 ) )
        functions.append( ParserFunction( "ABS", lambda l: abs( float( l ) ), 1 ) )
        functions.append( ParserFunction( "TRUNC", lambda l: int( l ), 1 ) )
        functions.append( ParserFunction( "ROUND", lambda l: round( float( l ) ), 1 ) )
        functions.append( ParserFunction( "SIGN", lambda l: 1 if float( l ) > 0 else -1 if float( l ) < 0 else 0, 1 ) )
        functions.append( ParserFunction( "PI", lambda: math.pi, 0 ) )
        functions.append( ParserFunction( "EXP", lambda l: math.exp( float( l ) ), 1 ) )
        
        self.functions = { }
        
        for f in functions:
            self.functions[ f.id ] = f
    
    
    def evaluate( self, stack ):
        # print( "evaluate: " + str( stack ) )
        op = stack.pop()
        
        if isinstance( op, ParserFunction ):
            f = op
            
            if f.arguments == 0:
                return f.function()
            elif f.arguments == 1:
                right = self.evaluate( stack )
                return f.function( right )
            elif f.arguments == 2:
                right = self.evaluate( stack )
                left = self.evaluate( stack )
                return f.function( left, right )
        elif op[ 0 ].isalpha():
            raise ValueError( "No such function as '{}'".format( op ) )
        else:
            return op


DEFAULT_FUNCTIONS = ParserFunctions()


class Parser:
    def pushFirst( self, _1, _2, tokens ):
        # print( "pushFirst", tokens )
        self.__stack.append( self.functions.functions.get( tokens[ 0 ] ) or tokens[ 0 ] )
    
    
    def pushUnary( self, _1, _2, tokens ):
        # print( "pushUnary", tokens )
        if tokens and tokens[ 0 ] == '-':
            self.__stack.append( self.functions.functions[ "@" + tokens[ 0 ] ] )


    # noinspection PyStatementEffect
    def __init__( self ):
        self.functions = DEFAULT_FUNCTIONS
        
        F_NUMBER = Combine( Word( "+-" + nums, nums )
                            + Optional( Literal( "." )
                                        + Optional( Word( nums ) ) )
                            + Optional( CaselessLiteral( "E" )
                                        + Word( "+-" + nums, nums ) ) )
        F_FUNCTIONS = None
        F_CONSTANTS = None
        
        F_LEFT = Literal( "(" ).suppress()
        R_RIGHT = Literal( ")" ).suppress()
        
        UNARY_PREFIX = None
        F_PRECEDENCE = [ ]
        
        for f in self.functions.functions.values():
            if f.precedence == -1:
                if UNARY_PREFIX is None:
                    UNARY_PREFIX = Literal( f.name )
                else:
                    UNARY_PREFIX |= Literal( f.name )
            elif f.precedence is not None:
                while len( F_PRECEDENCE ) <= f.precedence:
                    F_PRECEDENCE.append( None )
                
                if F_PRECEDENCE[ f.precedence ] is None:
                    F_PRECEDENCE[ f.precedence ] = Literal( f.name )
                else:
                    F_PRECEDENCE[ f.precedence ] |= Literal( f.name )
            elif f.arguments == 0:
                if F_CONSTANTS is None:
                    F_CONSTANTS = Literal( f.name )
                else:
                    F_CONSTANTS |= Literal( f.name )
            else:
                if F_FUNCTIONS is None:
                    F_FUNCTIONS = Literal( f.name )
                else:
                    F_FUNCTIONS |= Literal( f.name )
                    
        assert UNARY_PREFIX
        assert F_FUNCTIONS
        assert F_CONSTANTS
        assert F_PRECEDENCE
            
        expression = Forward()
        
        function_or_number = (F_CONSTANTS | F_NUMBER | F_FUNCTIONS + F_LEFT + expression + R_RIGHT).setParseAction( self.pushFirst )
        bracketed_thing = (F_LEFT + expression.suppress() + R_RIGHT)
        element = (Optional( UNARY_PREFIX ) + function_or_number | bracketed_thing).setParseAction( self.pushUnary )
        
        binary_ops = Forward()
        binary_ops << element + ZeroOrMore( (F_PRECEDENCE[ 0 ] + binary_ops).setParseAction( self.pushFirst ) )
        
        for p in F_PRECEDENCE[ 1: ]:
            binary_ops = binary_ops + ZeroOrMore( (p + binary_ops).setParseAction( self.pushFirst ) )
        
        expression << binary_ops
        self.__parser = expression
        self.__stack = [ ]
            
            
    def make_stack( self, text ):
        self.__stack = [ ]
        self.__parser.parseString( text )
        return list( self.__stack )
    
    
    def evaluate_stack( self, stack ):
        return self.functions.evaluate( list( stack ) )


PARSER = Parser()


class Equation:
    def __init__( self, text ):
        self.__stack = PARSER.make_stack( text )
    
    
    def evaluate( self ):
        return PARSER.evaluate_stack( self.__stack )
    
    
    def __str__( self ):
        return " ".join( str( x ) for x in reversed( self.__stack ) )


if __name__ == "__main__":
    def __test( text, expected ):
        print( "*** " + text )
        e = Equation( text )
        value = float( e.evaluate() )
        
        if value == expected:
            print( "GOOD EXPR={}, VALUE={}".format( text, value ) )
        else:
            print( "BAD EXPR={}, VALUE={}, EXPECTED={}".format( text, value, expected ) )
            raise ValueError( "Test failed." )
    
    
    __test( "9", 9 )
    __test( "-9", -9 )
    __test( "--9", 9 )
    __test( "0 - EXP(1)", -math.e )
    __test( "1e12", 1e12 )
    __test( "9 + 3 + 6", 9 + 3 + 6 )
    __test( "9 + 3 / 11", 9 + 3.0 / 11 )
    __test( "(9 + 3)", (9 + 3) )
    __test( "(9+3) / 11", (9 + 3.0) / 11 )
    __test( "9 - 12 - 6", 9 - 12 - 6 )
    __test( "9 - (12 - 6)", 9 - (12 - 6) )
    __test( "2*3.14159", 2 * 3.14159 )
    __test( "3.1415926535*3.1415926535 / 10", 3.1415926535 * 3.1415926535 / 10 )
    __test( "PI * PI / 10", math.pi * math.pi / 10 )
    __test( "PI*PI/10", math.pi * math.pi / 10 )
    __test( "PI^2", math.pi ** 2 )
    __test( "ROUND(PI^2)", round( math.pi ** 2 ) )
    __test( "6.02E23 * 8.048", 6.02E23 * 8.048 )
    __test( "EXP(1) / 3", math.e / 3 )
    __test( "SIN(PI/2)", math.sin( math.pi / 2 ) )
    __test( "TRUNC(EXP(1))", int( math.e ) )
    __test( "TRUNC(-EXP(1))", int( -math.e ) )
    __test( "ROUND(EXP(1))", round( math.e ) )
    __test( "ROUND(-EXP(1))", round( -math.e ) )
    __test( "EXP(1)^PI", math.e ** math.pi )
    __test( "2^3^2", 2 ** 3 ** 2 )
    __test( "2^3+2", 2 ** 3 + 2 )
    __test( "2^9", 2 ** 9 )
    __test( "SIGN(-2)", -1 )
    __test( "SIGN(0)", 0 )
    __test( "SIGN(0.1)", 1 )
