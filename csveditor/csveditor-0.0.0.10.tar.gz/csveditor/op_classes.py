import re
from typing import List, cast, Iterable
from collections import Counter, defaultdict

from csveditor.tables import ColumnId, TableId, State
from csveditor import parser
from mhelper import string_helper as StringHelper, MEnum, SwitchError


class ESortMode( MEnum ):
    """
    :data ALPHA: Sort by text
    :data NUMERICAL: Sort by number
    """
    ALPHA = 1
    NUMERICAL = 2


class EMissing( MEnum ):
    """
    :data BLANK: Set the value to empty
    :data DROP:  Drop the row
    :data ERROR: Stop and raise an error
    """
    BLANK = 0
    DROP = 1
    ERROR = 2


class EFilter( MEnum ):
    """
    For filters 𝔁 is the column value and 𝔂 is the provided value. The result determines the filter status.
    For applications 𝔁 is the destination and 𝔂 is the source. The result is stored in the destination, 𝔁.
    
    : data N_EQ   : ~numeric~ Equal to (𝔁 = 𝔂)
    : data N_NEQ  : ~numeric~ Not equal to (𝔁 ≠ 𝔂)
    : data N_LT   : ~numeric~ Less than (𝔁 < 𝔂)
    : data N_LTE  : ~numeric~ Less than or equal to (𝔁 ≤ 𝔂)
    : data N_GT   : ~numeric~ Greater than (𝔁 > 𝔂)
    : data N_GTE  : ~numeric~ Greater than or equal to (𝔁 ≥ 𝔂)
    : data N_SUM  : ~numeric-op~ Add (𝔁 + 𝔂)
    : data N_SUB  : ~numeric-op~ Subtract (𝔁 - 𝔂)
    : data N_DIV  : ~numeric-op~ Divide (𝔁 / 𝔂)
    : data N_MUL  : ~numeric-op~ Multiply (𝔁 * 𝔂)
    : data N_MOD  : ~numeric-op~ Modulo (𝔁 % 𝔂)
    : data S_IN   : ~string~ Contains (𝔁 ∋ 𝔂)
    : data S_RE   : ~string~ Regular expression (x ≡ y)
    : data S_EQ   : ~string~ Equal to (𝔁 = 𝔂)
    : data S_NEQ  : ~string~ Equal to (𝔁 ≠ 𝔂)
    : data S_LTE  : ~string~ Equal to or comes before (𝔁 ≤ 𝔂)
    : data S_GTE  : ~string~ Equal to or comes after (𝔁 ≤ 𝔂)
    : data S_LT   : ~string~ Comes before (𝔁 < 𝔂)
    : data S_GT   : ~string~ Comes after (𝔁 > 𝔂)
    : data S_CAT  : ~string-op~ Concatenate (𝔁 ⨝ 𝔂)
    : data L_AND  : ~logical-op~ And (𝔁 ∧ 𝔂)
    : data L_OR   : ~logical-op~ Or (𝔁 ∨ 𝔂)
    : data L_NOT  : ~logical-op~ Not (¬ 𝔂)
    : data L_XOR  : ~logical-op~ Xor (𝔁 ⊻ 𝔂)
    : data D_NOP  : ~direct-op~ No operation (𝔁)
    : data D_COPY : ~direct-op~ Copy value (𝔂)
    """
    N_EQ = 1
    N_NEQ = 2
    N_LT = 3
    N_LTE = 4
    N_GT = 5
    N_GTE = 6
    S_IN = 7
    S_RE = 8
    S_EQ = 9
    S_NEQ = 10
    S_LTE = 11
    S_GTE = 12
    S_LT = 13
    S_GT = 14
    D_NOP = 15
    D_COPY = 16
    N_SUM = 17
    N_SUB = 18
    N_DIV = 19
    N_MUL = 20
    N_MOD = 21
    L_AND = 22
    L_OR = 23
    L_NOT = 24
    L_XOR = 25
    S_CAT = 26


class Operation:
    def run( self, state: State ):
        raise NotImplementedError( "abstract" )


class RowOperation:
    def run( self, state: State ):
        self.prepare( state.headers )
        
        index = state.start_index
        
        to_remove = [ ]
        
        for local_index, row in enumerate( state.rows ):
            if self.commit( index, row ) is False:
                to_remove.append( local_index )
            
            index += 1
        
        for local_index in reversed( to_remove ):
            del state.rows[ local_index ]
    
    
    def prepare( self, headers: List[ str ] ):
        pass
    
    
    def commit( self, index: int, row: List[ str ] ):
        raise NotImplementedError( "abstract" )


def pass_through( x ):
    return x


class LookupOperation( RowOperation ):
    def __init__( self, target: ColumnId, source: TableId, find: ColumnId, replace: ColumnId, missing: EMissing ):
        self.target = target
        self.source = source
        self.find = find
        self.replace = replace
        self.preloaded = False
        self.missing = missing
        
        self.prep_target_index = None
        self.prep_dictionary = None
        self.prep_find_index = None
        self.prep_replace_index = None
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_target_index = self.target.index( headers )
        
        self.prep_dictionary = { }
        
        prep_source = self.source.table.final_rows()
        
        prep_find_index = self.find.index( prep_source.headers )
        prep_replace_index = self.replace.index( prep_source.headers )
        
        for row in prep_source.rows:
            self.prep_dictionary[ row[ prep_find_index ] ] = row[ prep_replace_index ]
    
    
    def commit( self, index: int, row: List[ str ] ):
        value = self.prep_dictionary.get( row[ self.prep_target_index ] )
        
        if value is None:
            if self.missing == EMissing.BLANK:
                value = ""
            elif self.missing == EMissing.DROP:
                return
            elif self.missing == EMissing.ERROR:
                raise ValueError( "No such key as '{}' in {} keys.".format( row[ self.prep_target_index ], len( self.prep_dictionary ) ) )
            else:
                raise SwitchError( "missing", self.missing )
        
        row[ self.prep_target_index ] = value
    
    
    def __str__( self ):
        return "LOOKUP '{0}' FROM '{1}:{2}' AND '{1}:{3}', {4} ON MISSING".format( self.target, self.source, self.find, self.replace, self.missing )


class JoinOperation( Operation ):
    def __init__( self, left_column: ColumnId, right_table: TableId, right_column: ColumnId, missing: EMissing, rename = "*" ):
        self.left_join = left_column
        self.right_table = right_table
        self.right_join = right_column
        self.missing = missing
        self.rename = rename
    
    
    def run( self, state: State ):
        right_state = self.right_table.table.final_rows()
        left_headers = state.headers
        right_join_index = self.right_join.index( right_state.headers )
        left_join_index = self.left_join.index( left_headers )
        dictionary = defaultdict( list )
        
        for index, row in enumerate( right_state.rows ):
            value = row[ right_join_index ]
            del row[ right_join_index ]
            dictionary[ value ].append( row )
        
        del right_state.headers[ right_join_index ]
        
        if self.rename:
            left_headers.extend( self.rename.replace( "*", x ) for x in right_state.headers )
        else:
            left_headers.extend( right_state.headers )
        
        result = [ ]
        
        for row in state.rows:
            value = row[ left_join_index ]
            
            new_rows = dictionary.get( value )
            
            if new_rows is not None:
                for new_row in new_rows:
                    result.append( row + new_row )
            elif self.missing == EMissing.BLANK:
                result.append( row + [ "" for _ in right_state.headers ] )
            elif self.missing == EMissing.DROP:
                pass
            elif self.missing == EMissing.ERROR:
                raise ValueError( "Missing key '{}' in lookup.".format( value ) )
            else:
                raise SwitchError( "missing", self.missing )
        
        state.rows = result
    
    
    def __str__( self ):
        return "JOIN ON COLUMN '{}' TO '{}':'{}', {} ON MISSING".format( self.left_join, self.right_table, self.right_join, self.missing )


class ReplaceOperation( RowOperation ):
    def __init__( self, column_id: ColumnId, find: str, replace: str ):
        self.column_id = column_id
        self.find = find
        self.replace = replace
        
        self.prep_column_index = None
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_column_index = self.column_id.index( headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        row[ self.prep_column_index ] = row[ self.prep_column_index ].replace( self.find, self.replace )
    
    
    def __str__( self ):
        return "IN '{}' REPLACE '{}' WITH '{}'".format( self.column_id, self.find, self.replace )


class ReplaceRxOperation( RowOperation ):
    def __init__( self, column_id: ColumnId, find: str, replace: str ):
        self.column_id = column_id
        self.find = re.compile( find )
        self.replace = replace
        
        self.prep_column_index = None
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_column_index = self.column_id.index( headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        row[ self.prep_column_index ] = self.find.sub( self.replace, row[ self.prep_column_index ] )
    
    
    def __str__( self ):
        return "IN '{}' RX REPLACE '{}' WITH '{}'".format( self.column_id, self.find.pattern, self.replace )


class SwapOperation( RowOperation ):
    def __init__( self, a: ColumnId, b: ColumnId ):
        self.a = a
        self.b = b
        
        self.a_index = None
        self.b_index = None
    
    
    def prepare( self, headers: List[ str ] ):
        self.a_index = self.a.index( headers )
        self.b_index = self.b.index( headers )
        self.commit( cast( int, None ), headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        oa = row[ self.a_index ]
        row[ self.a_index ] = row[ self.b_index ]
        row[ self.b_index ] = oa
    
    
    def __str__( self ):
        return "SWAP '{}' AND '{}'".format( self.a, self.b )


class RenameHeaderOperation( RowOperation ):
    def __init__( self, column_id: ColumnId, new_name: str ):
        self.column_id = column_id
        self.new_name = new_name
    
    
    def prepare( self, headers: List[ str ] ):
        prep_column_index = self.column_id.index( headers )
        headers[ prep_column_index ] = self.new_name
    
    
    def commit( self, index: int, row: List[ str ] ):
        pass
    
    
    def __str__( self ):
        return "RENAME HEADER '{}' TO '{}'".format( self.column_id, self.new_name )


class SortOperation( Operation ):
    def __init__( self, column: ColumnId, mode: ESortMode ):
        self.column = column
        self.mode = mode
    
    
    def run( self, state: State ):
        index = self.column.index( state.headers )
        
        if self.mode == ESortMode.ALPHA:
            state.rows = sorted( state.rows, key = lambda x: float( x[ index ] ) )
        elif self.mode == ESortMode.NUMERICAL:
            state.rows = sorted( state.rows, key = lambda x: x[ index ] )
        else:
            raise SwitchError( "mode", self.mode )


class UniqueOperation( RowOperation ):
    def __init__( self, column: ColumnId, count: int ):
        self.column = column
        self.count = count
        
        self.prep_index = -1
        self.prep_counter = Counter()
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_index = self.column.index( headers )
        self.prep_counter = Counter()
    
    
    def commit( self, index: int, row: List[ str ] ):
        current = row[ self.prep_index ]
        self.prep_counter[ current ] += 1
        
        return self.prep_counter[ current ] <= self.count


class UniqueUnixOperation( RowOperation ):
    def __init__( self, column: ColumnId, count: int ):
        self.column = column
        self.count = count
        
        self.prep_index = -1
        self.prep_last = None
        self.prep_count = 0
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_index = self.column.index( headers )
        self.prep_last = None
        self.prep_count = 0
    
    
    def commit( self, index: int, row: List[ str ] ):
        current = row[ self.prep_index ]
        
        if current == self.prep_last:
            self.prep_count += 1
        else:
            self.prep_last = current
            self.prep_count = 0
        
        return self.prep_count <= self.count


class DropColOperation( RowOperation ):
    def __init__( self, cols: Iterable[ ColumnId ] ):
        self.cols = list( cols )
        self.prep_col_indexes = [ -1 ]
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_col_indexes = list( reversed( sorted( x.index( headers ) for x in self.cols ) ) )
        self.commit( -1, headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        for index in self.prep_col_indexes:
            del row[ index ]
    
    
    def __str__( self ):
        return "DROP COLUMNS {}".format( ", ".join( str( x ) for x in self.cols ) )


class DropRowOperation( Operation ):
    def __init__( self, start: int, end: int ):
        self.start = start
        self.end = end
    
    
    def run( self, state: State ):
        del state.rows[ self.start:self.end ]


class Filter:
    """
    Represents a simple filter.
    
    :data filter_id:  Filter ID passed in.
    :data v_function: Function on the variable value (v)
    :data u_function: Function on the fixed value (u)
    :data f_function: Filter function (variable (v), fixed (u)) -> bool.
    """
    
    
    def __init__( self, filter: EFilter ):
        self.filter_id = filter
        
        if filter == EFilter.N_EQ:
            self.v_function = float
            self.f_function = lambda v, u: v == u
        elif filter == EFilter.N_NEQ:
            self.v_function = float
            self.f_function = lambda v, u: v != u
        elif filter == EFilter.N_GT:
            self.v_function = float
            self.f_function = lambda v, u: v > u
        elif filter == EFilter.N_GTE:
            self.v_function = float
            self.f_function = lambda v, u: v >= u
        elif filter == EFilter.N_LT:
            self.v_function = float
            self.f_function = lambda v, u: v < u
        elif filter == EFilter.N_LTE:
            self.v_function = float
            self.f_function = lambda v, u: v <= u
        elif filter == EFilter.S_EQ:
            self.v_function = str
            self.f_function = lambda v, u: v == u
        elif filter == EFilter.S_NEQ:
            self.v_function = str
            self.f_function = lambda v, u: v != u
        elif filter == EFilter.S_LT:
            self.v_function = str
            self.f_function = lambda v, u: v < u
        elif filter == EFilter.S_LTE:
            self.v_function = str
            self.f_function = lambda v, u: v <= u
        elif filter == EFilter.S_GT:
            self.v_function = str
            self.f_function = lambda v, u: v > u
        elif filter == EFilter.S_GTE:
            self.v_function = str
            self.f_function = lambda v, u: v >= u
        elif filter == EFilter.S_RE:
            self.v_function = str
            self.u_function = re.compile
            self.f_function = lambda v, u: u.match( v )
        elif filter == EFilter.D_NOP:
            self.v_function = pass_through
            self.f_function = lambda v, u: v
        elif filter == EFilter.D_COPY:
            self.v_function = pass_through
            self.f_function = lambda v, u: u
        elif filter == EFilter.ADD:
            self.v_function = float
            self.f_function = lambda v, u: v + u
        elif filter == EFilter.N_DIV:
            self.v_function = float
            self.f_function = lambda v, u: v / u
        elif filter == EFilter.N_MUL:
            self.v_function = float
            self.f_function = lambda v, u: v * u
        elif filter == EFilter.N_SUB:
            self.v_function = float
            self.f_function = lambda v, u: v - u
        elif filter == EFilter.N_MOD:
            self.v_function = float
            self.f_function = lambda v, u: v % u
        elif filter == EFilter.AND:
            self.v_function = StringHelper.to_bool
            self.f_function = lambda v, u: v and u
        elif filter == EFilter.OR:
            self.v_function = StringHelper.to_bool
            self.f_function = lambda v, u: v or u
        elif filter == EFilter.XOR:
            self.v_function = StringHelper.to_bool
            self.f_function = lambda v, u: v ^ u
        elif filter == EFilter.S_CAT:
            self.v_function = str
            self.f_function = lambda v, u: v + u
        else:
            raise SwitchError( "filter", filter )
        
        if not hasattr( self, "u_function" ):
            self.u_function = self.v_function
    
    
    def __str__( self ):
        return "{}".format( self.filter_id )


class ApplyOperation( RowOperation ):
    def __init__( self, dest: ColumnId, source: ColumnId, filter: Filter ):
        self.dest = dest
        self.source = source
        self.filter = filter
        self.prep_dest_index = -1
        self.prep_source_index = -1
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_dest_index = self.dest.index( headers )
        self.prep_source_index = self.source.index( headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        f = self.filter
        row[ self.prep_dest_index ] = f.f_function( f.v_function( row[ self.prep_dest_index ] ), f.u_function( row[ self.prep_source_index ] ) )
    
    
    def __str__( self ):
        return "SET {} {} {}".format( self.dest, self.filter, self.source )


class FilterOperation( RowOperation ):
    def __init__( self, column: ColumnId, value: str, filter: Filter ):
        self.column = column
        self.filter = filter
        self.u_value = filter.v_function( value )
        self.prep_index = -1
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_index = self.column.index( headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        return self.filter.f_function( row[ self.prep_index ], self.u_value )
    
    
    def __str__( self ):
        return "FILTER {} {} {}".format( self.column, self.filter, self.u_value )


class CustomOperation( RowOperation ):
    def __init__( self, column: ColumnId, expression: str ):
        self.column = column
        self.expression = expression
        self.prep_column_index = -1
        self.prep_equation = parser.Equation( self.expression )
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_column_index = self.column.index( headers )
        self.prep_equation = parser.Equation( self.expression )
    
    
    def commit( self, index: int, row: List[ str ] ):
        row[ self.prep_column_index ] = self.prep_equation.evaluate()


class AddOperation( RowOperation ): #temporary delete me
    def __init__( self, column: ColumnId, to_add: ColumnId, format: str ):
        self.column = column
        self.to_add = to_add
        self.format = format
        self.prep_column_index = -1
        self.prep_to_add_index = -1
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_column_index = self.column.index( headers )
        self.prep_to_add_index = self.to_add.index( headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        row[ self.prep_column_index ] = self.format.format( row[ self.prep_column_index ], row[ self.prep_to_add_index ] )


class PadOperation( RowOperation ):
    def __init__( self, default: str ):
        self.default = default
        self.prep_num_headers = -1
    
    
    def prepare( self, headers: List[ str ] ):
        self.prep_num_headers = len( headers )
    
    
    def commit( self, index: int, row: List[ str ] ):
        missing = self.prep_num_headers - len( row )
        
        if missing:
            row += [ self.default ] * missing
    
    
    def __str__( self ):
        return "PAD WITH '{}'".format( self.default )
