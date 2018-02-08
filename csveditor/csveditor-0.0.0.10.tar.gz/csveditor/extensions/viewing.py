from typing import Optional
from collections import Counter

from colorama import Fore, Back, Style

from csveditor import tables
from csveditor.parser import Equation
from csveditor.tables import ColumnAndTableId
from intermake import MCMD, command
from mhelper import string_helper

from csveditor.op_classes import Filter, EFilter


@command()
def summary():
    """
    Prints a summary of the current table.
    """
    table = tables.current()
    fr = tables.current().final_rows()
    
    MCMD.information( "Initial: {} rows".format( len( table.table ) - (1 if table.dialect.header else None) ) )
    MCMD.information( "Initial: {} columns".format( len( table.first_header() ) ) )
    MCMD.information( "Final: {} rows".format( len( fr.rows ) ) )
    MCMD.information( "Final: {} columns".format( len( fr.headers ) ) )


@command()
def find( id: ColumnAndTableId, filter: EFilter, value: str, count: bool = True, print: bool = True ):
    """
    Searches for text in the specified column and prints out the matching rows.
    
    :param print:    Print the matching rows
    :param count:    Count the matching rows 
    :param filter:   Filter to exact.
    :param value:    Regular expression 
    :param id:      Name of the column
    """
    state = id.table_id.table.final_rows()
    
    filter = Filter( filter )
    value = filter.u_function( value )
    
    MCMD.information( "{} {} {}".format( id.column_id, filter, value ) )
    
    col_index = id.column_id.index( state.headers )
    
    stt = [ ]
    count_ = 0
    
    for index, row in enumerate( state.rows ):
        if filter.f_function( filter.v_function( row[ col_index ] ), value ):
            if print:
                _print_row( index, state.headers, row, stt )
            
            count_ += 1
    
    if count:
        MCMD.information( '"{}" x {}'.format( filter, Fore.GREEN + str( count_ ) + Fore.RESET ) )


@command()
def factor( id: ColumnAndTableId, simple: bool = False ):
    """
    View the unique values of the specified column.
    
    :param simple: Simple printout
    :param id: Column to view 
    """
    state = id.table_id.table.final_rows()
    
    col_index = id.column_id.index( state.headers )
    
    c = Counter()
    
    for row in state.rows:
        c[ row[ col_index ] ] += 1
    
    r = [ ]
    lv = None
    cnt = 0
    
    if simple:
        MCMD.print( "id,count" )
    
    for k, v in sorted( c.items(), key = lambda kvp: kvp[ 1 ] ):
        if simple:
            MCMD.print( "{},{}".format( k, v ) )
        else:
            if v == lv:
                r.append( ", " + Back.WHITE + Fore.BLACK + k + Style.RESET_ALL )
                cnt += 1
            else:
                if cnt != 0:
                    r.append( " ({})".format( Fore.RED + str( cnt ) + Fore.RESET ) )
                r.append( "\n" )
                r.append( Fore.GREEN + str( v ) + Fore.RESET + ": " + Back.WHITE + Fore.BLACK + k + Style.RESET_ALL )
                cnt = 1
            
            lv = v
    
    if not simple:
        if cnt != 0:
            r.append( " ({})".format( Fore.RED + str( cnt ) + Fore.RESET ) )
        
        MCMD.print( "".join( r ) )
        
        MCMD.print( "There are {} factors.".format( len( c ) ) )


@command()
def raw( index: int = 1 ):
    """
    Displays the raw text for the specified row.
    
    :param index: Index of row to display.
    """
    MCMD.print( string_helper.special_to_symbol( tables.current().raw_row( index ) ) )


@command()
def head( n: int = 1 ):
    """
    Displays the top `n` rows of the table.
    :param n:    Number of rows to show.
    """
    view( n = n )


@command()
def tail( n: int = 1 ):
    """
    Displays the last `n` rows of the table.
    :param n:    Number of rows to show.
    """
    table = tables.current()
    view( start = len( table.table ) - n, n = n )


@command()
def header():
    """
    Displays the head of the current table.
    """
    view( n = 0, header = True )


@command()
def view( start: int = 0, end: Optional[ int ] = None, n: int = 1, header: bool = False ):
    """
    Displays the top row of the current table.
    
    :param n:       Number of rows to display 
    :param start:   First row to display 
    :param end:     Last row to display (overrides `n`) 
    :param header:  Display the header row?
    :return: 
    """
    table = tables.current()
    
    if end is None:
        if n == -1:
            end = -1
        else:
            end = start + n
    
    state = table.final_rows()
    stt = [ ]
    
    if header:
        _print_row( "HEADER", state.headers, None, stt )
    
    index = start
    
    for row in state.rows[ start:end ]:
        _print_row( index, state.headers, row, stt )
        
        index += 1


@command()
def calc( expression: str ):
    """
    Calculates the expression.
    :param expression: Expression. 
    :return: 
    """
    eq = Equation( expression )
    MCMD.information( "{} = {}".format( eq, eq.evaluate() ) )

MAX_VALUE_LEN = 10000

def _print_row( row_index, headers_, row, state = None ):
    MCMD.print( style_row( row_index ) )
    
    if row is None:
        MCMD.print( "CELLS: 0" )
        row = [ None for _ in headers_ ]
    else:
        MCMD.print( "CELLS: " + str( len( row ) ) )
    
    for col_index, value in enumerate( row ):
        if state is None:
            state = [ ]
        
        if not state:
            i_width = max( len( str( x ) ) for x in range( len( headers_ ) ) ) + 1
            h_width = max( len( x ) for x in headers_ ) + 1
            state = [ i_width, h_width ]
        
        i_width = state[ 0 ]
        h_width = state[ 1 ]
        header_text = headers_[ col_index ]
        
        if value is None:
            value = ""
        elif len( str( value ) ) == 0:
            value = Back.LIGHTBLACK_EX + Fore.WHITE + "(none)" + Style.RESET_ALL
        else:
            value = string_helper.special_to_symbol( value )
            
            value = str( value )
            
            if len( value ) > MAX_VALUE_LEN:
                value = value[ :MAX_VALUE_LEN ] + "..."
        
        MCMD.print( style_index( str( col_index ), i_width ) + style_name( header_text, h_width ) + style_value( value ) )


def style_name( x, w ):
    s = " " * (w - len( x ))
    return Fore.RED + Back.WHITE + x + Style.RESET_ALL + s


def style_index( x, w ):
    s = " " * (w - len( x ))
    return Fore.BLUE + Back.WHITE + x + Style.RESET_ALL + s


def style_value( x ):
    return Fore.BLACK + Back.WHITE + x + Style.RESET_ALL


def style_row( x ):
    return Fore.WHITE + Back.BLUE + "-" * 20 + " {} ".format( x ) + "-" * 20 + Style.RESET_ALL
