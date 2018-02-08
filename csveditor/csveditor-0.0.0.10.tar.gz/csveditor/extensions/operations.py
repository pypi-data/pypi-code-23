from typing import Optional, List

from intermake import MCMD, command, Theme, help_command
from mhelper import array_helper

from csveditor import op_classes, tables
from csveditor.op_classes import EFilter, EMissing, ESortMode, Filter
from csveditor.tables import ColumnAndTableId, TableId


@command()
def ops():
    """
    Displays the list of operations on the current table.
    """
    __view_ops()


@help_command()
def operational_help():
    """
    To specify a column use the column name:
    
        `artist`
        
    Or the index:
    
        `#1`
        
    You can specify the table name too:
    
        `records:artist`
        
    To specify multiple columns, use comma:
    
        `artist,#2,records:album` 
    """
    pass



def __view_ops( highlight = None, removed = False ):
    table = tables.current()
    
    MCMD.print( table )
    
    if not tables.current().operations:
        MCMD.print( "No operations." )
    
    for index, op in enumerate( table.operations ):
        if op is highlight:
            if not removed:
                suffix = " " + Theme.STATUS_YES + "✔" + Theme.RESET
            else:
                suffix = " " + Theme.STATUS_NO + "✘" + Theme.RESET
        else:
            suffix = ""
        
        MCMD.information( "{}. {}".format( index, op ) + suffix )


@command()
def drop_op( index: int ):
    """
    Removes an operation.
    :param index:   Index of the operation to drop.
    """
    op = tables.current().operations[ index ]
    __view_ops( highlight = op, removed = True )
    del tables.current().operations[ index ]


@command()
def lookup( target: ColumnAndTableId, key: ColumnAndTableId, value: ColumnAndTableId, missing: EMissing = EMissing.ERROR ):
    """
    Looks up the text in one column in another column (the "key"), and replaces that with a corresponding value.
    
    :param target:      Affected column. 
    :param key:         Column to acquire the keys 
    :param value:       Column to acquire the values 
    :param missing:     Missing key behaviour 
    """
    if key.table_id.table != value.table_id.table:
        raise ValueError( "Cannot specify two different tables for key ('{}') and value ('{}').".format( key.table_id.table, value.table_id.table ) )
    
    op = op_classes.LookupOperation( target.column_id, key.table_id, key.column_id, value.column_id, missing )
    target.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def setval( target: ColumnAndTableId, expression: str ):
    """
    Uses a Python expression to modify the table.
    :param target:      Target table 
    :param expression:  Expression. 
    """
    op = op_classes.CustomOperation( target.column_id, expression )
    target.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def pad( target: TableId, default: str = "" ):
    """
    Pads out missing cells.
    :param target:  Table to modify
    :param default: What to pad with 
    :return:  
    """
    op = op_classes.PadOperation( default )
    target.table.operations.append( op )
    __view_ops( op )


@command()
def replace( target: ColumnAndTableId, find: str, replace: str, regex: bool = False ):
    """
    In a specific column, finds text and replaces it with some other text.
    
    :param target:    Affected column. 
    :param find:      Text to find.
    :param replace:   Text to replace.
                      Note: If using regular expressions you can use {0} to represent the capture groups.
    :param regex:     Whether to use regular expressions.  
    """
    # Allow {x} to represent group number in replacement
    for i in range( 0, 10 ):
        replace = replace.replace( "{" + str( i ) + "}", "\g<" + str( i ) + ">" )
    
    if regex:
        op = op_classes.ReplaceOperation( target.column_id, find, replace )
    else:
        op = op_classes.ReplaceRxOperation( target.column_id, find, replace )
    
    target.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def swap( a: ColumnAndTableId, b: ColumnAndTableId ):
    """
    Swaps the values and headers of two columns.
    
    :param a:   First affected column.
    :param b:   Second affected column.
    """
    if a.table_id != b.table_id:
        raise ValueError( "a and b must be in the same table." )
    
    op = op_classes.SwapOperation( a.column_id, b.column_id )
    a.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def drop_row( start: int, end: Optional[ int ] = None, count: Optional[ int ] = None ):
    """
    Removes the row with the specified index from the table.
    
    :param start: Index of first row to drop.
    :param end:   Index one beyond the last row to drop. 
    :param count: Number of rows to drop. Defaults to 1. 
    """
    if end is None:
        if count is None:
            end = start + 1
        else:
            end = start + count
    elif count is not None:
        raise ValueError( "Cannot specify both the `end` and `count` parameters." )
    
    op = op_classes.DropRowOperation( start, end )
    tables.current().operations.append( op )
    __view_ops( op )


@command()
def drop_col( ids: List[ ColumnAndTableId ] ):
    """
    Drops columns from the table.
    :param ids: One or more column IDs 
    :return: 
    """
    if not ids:
        raise ValueError( "At least one column must be specified." )
    
    for left, right in array_helper.lagged_iterate( ids ):
        if left.table_id != right.table_id:
            raise ValueError( "All columns must be in the same table." )
    
    op = op_classes.DropColOperation( (x.column_id for x in ids) )
    ids[ 0 ].table_id.table.operations.append( op )
    __view_ops( op )


@command()
def filter( col: ColumnAndTableId, filter: EFilter, value: str ):
    """
    Filters the table on the value of specific column.
    
    :param col:     Column by which to filter
    :param filter:  Filter mode
    :param value:   Value to filter by
    """
    op = op_classes.FilterOperation( col.column_id, value, Filter( filter ) )
    col.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def sort( col: ColumnAndTableId, mode: ESortMode = ESortMode.NUMERICAL ):
    """
    Sorts the table by a specific column.
    
    :param col: Column
    :param mode: Sort mode 
    :return: 
    """
    op = op_classes.SortOperation( col.column_id, mode )
    col.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def unique_u( col: ColumnAndTableId, count: int = 1 ):
    """
    Removes non-unique elements from the table.
    
    Like the unix function `uniq`, this assumes the column is sorted and identical elements appear together.
    See `sort` and `unique`.
    
    :param col:     Column to filter. 
    :param count:   Number of unique elements to keep.
    :return: 
    """
    op = op_classes.UniqueUnixOperation( col.column_id, count )
    col.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def unique( col: ColumnAndTableId, count: int = 1 ):
    """
    Removes non-unique elements from the table.
    
    Unlike `unique_u` this does not assume that the column has been pre-sorted.
    
    :param col:     Column to filter 
    :param count:   Number of unique elements to keep. 
    :return: 
    """
    op = op_classes.UniqueOperation( col.column_id, count )
    col.table_id.table.operations.append( op )
    __view_ops( op )
    
@command()
def add( a: ColumnAndTableId, b: ColumnAndTableId, format:str ):
    """
    Removes non-unique elements from the table.
    
    Unlike `unique_u` this does not assume that the column has been pre-sorted.
    
    :param a:     First column and target
    :param b:   Second column
    :param format: Format, in Python format. 
    :return: 
    """
    if a.table_id != b.table_id:
        raise ValueError( "a and b must be in the same table." )
    
    op = op_classes.AddOperation( a.column_id, b.column_id, format )
    a.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def rename( col: ColumnAndTableId, name: str ):
    """
    Renames a column
    
    :param col:     Column to rename 
    :param name:    New name 
    :return: 
    """
    op = op_classes.RenameHeaderOperation( col.column_id, name )
    col.table_id.table.operations.append( op )
    __view_ops( op )


@command()
def join( left: ColumnAndTableId, right: ColumnAndTableId, missing: EMissing = EMissing.ERROR, rename: Optional[ str ] = None ):
    """
    Finds columns in the table matching those in another table, adding rows from the second table as appropriate.
    
    :param left:            Column to obtain lookup text from
    :param right:           Column to search for lookup text
    :param missing:         Missing value behaviour. 
    :param rename:          Name of the new columns to be added to the left table, where '*' is the name of the column in the right table.
    """
    if rename is not None and not "*" in rename:
        raise ValueError( "The `rename` parameter should contain the original name placeholder, '*'." )
    
    op = op_classes.JoinOperation( left.column_id, right.table_id, right.column_id, missing, rename )
    left.table_id.table.operations.append( op )
    __view_ops( op )
