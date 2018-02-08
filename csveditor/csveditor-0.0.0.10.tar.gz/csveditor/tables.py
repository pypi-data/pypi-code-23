import csv
from typing import List

from mhelper import MEnum


class State:
    def __init__( self, headers: List[ str ], start_index: int, rows: List[ List[ str ] ] ):
        self.headers = headers
        self.start_index = start_index
        self.rows = rows


class EQuote( MEnum ):
    QUOTE_ALL = 1 #type: EQuote
    QUOTE_MINIMAL = 0 #type: EQuote
    QUOTE_NONE = 3 #type: EQuote
    QUOTE_NON_NUMERIC = 2 #type: EQuote


class TableDialect:
    def __init__( self ):
        self.delimiter = ","
        self.quotechar = '"'
        self.escapechar = None
        self.doublequote = True
        self.skipinitialspace = False
        self.lineterminator = "\n"
        self.quote_mode = EQuote.QUOTE_MINIMAL
        self.header = True
        self.trim = False
    
    
    @property
    def quoting( self ):
        return self.quote_mode.value
    
    
    @quoting.setter
    def quoting( self, value ):
        self.quote_mode = EQuote( value )
    
    
    def __str__( self ):
        r = [ ]
        
        if self.delimiter == ",":
            r.append( "CSV-like" )
        elif self.delimiter == "\t":
            r.append( "TSV-like" )
        else:
            r.append( "Custom" )
        
        return "".join( r )


class Table:
    def __init__( self ):
        self.file_name = ""
        self.accession = "default"
        self.operations = [ ]
        self.table = [ [ ] ]  # type: List[List[str]]
        self.header_row = ""
        self.has_header_row = False
        self.dialect = TableDialect()
        self.out_dialect = None  # type: TableDialect
    
    
    def __str__( self ):
        return 'Table "{}": {}'.format( self.accession, self.file_name or "(not saved)" )
    
    
    def load( self, detect_dialect = True ):
        self.table = [ ]
        
        with open( self.file_name ) as file:
            if detect_dialect:
                try:
                    sample_dialect = csv.Sniffer().sniff( file.read( 1024 ) )
                    self.dialect.delimiter = sample_dialect.delimiter
                    self.dialect.doublequote = sample_dialect.doublequote
                    self.dialect.escapechar = sample_dialect.escapechar
                    self.dialect.lineterminator = sample_dialect.lineterminator
                    self.dialect.quotechar = sample_dialect.quotechar
                    self.dialect.quoting = sample_dialect.quoting
                    self.dialect.skipinitialspace = sample_dialect.skipinitialspace
                except:
                    self.dialect.delimiter = ','
                    self.dialect.doublequote = True
                    self.dialect.escapechar = None
                    self.dialect.lineterminator = '\n'
                    self.dialect.quotechar = '"'
                    self.dialect.quoting = EQuote.QUOTE_MINIMAL
                    self.dialect.skipinitialspace = True
                
                file.seek( 0 )
            
            top_line = next( file )
            self.has_header_row = self.dialect.header
            
            if self.dialect.header:
                self.header_row = top_line
            else:
                self.table.append( top_line )
                self.header_row = None
            
            for line in file:
                self.table.append( line )
    
    
    def place_header( self ):
        if self.dialect.header == self.has_header_row:
            return
        
        self.has_header_row = self.dialect.header
        
        if self.dialect.header:
            # Has a header, didn't before
            self.header_row = self.table[ 0 ]
            del self.table[ 0 ]
        else:
            # Has a header, doesn't now
            self.table.insert( 0, self.header_row )
            self.header_row = None
    
    
    def save( self ):
        dialect = self.out_dialect if self.out_dialect else self.dialect
        
        with open( self.file_name, "w" ) as file:
            writer = csv.writer( file, dialect = dialect )
            
            state = self.final_rows()
            
            if dialect.header:
                writer.writerow( state.headers )
            
            for row in state.rows:
                writer.writerow( row )
    
    
    def row( self, index ) -> List[ str ]:
        return csv.reader( self.table[ index:index + 1 ], dialect = self.dialect )
    
    
    def final_rows( self ) -> State:
        state = State( headers = self.first_header(),
                       start_index = 0,
                       rows = [ next( csv.reader( [ row_text ], dialect = self.dialect ) ) for row_text in self.table ] )
        
        if self.dialect.trim:
            for i in range( len( state.rows ) ):
                state.rows[ i ] = [ x.strip() for x in state.rows[ i ] ]
        
        for operation in self.operations:
            operation.run( state )
        
        return state
    
    
    def raw_row( self, index ) -> List[ str ]:
        return self.table[ index ]
    
    
    def first_header( self ):
        if self.dialect.header:
            r = next( csv.reader( [ self.header_row ], dialect = self.dialect ) )
            
            if self.dialect.trim:
                r = [ x.strip() for x in r ]
            
            return r
        else:
            top = next( csv.reader( [ self.table[ 0 ] ], dialect = self.dialect ) )
            return [ "V" + str( i ) for i, _ in enumerate( top ) ]


class TableId:
    def __init__( self, accession: str ):
        self.table_ac = accession
    
    
    @property
    def table( self ):
        if self.table_ac == ".":
            return _top_file
        elif self.table_ac:
            return get_file( self.table_ac )
        else:
            return _top_file
    
    
    def __eq__( self, other ):
        return self.table_ac == other.table_ac
    
    
    def __str__( self ):
        return self.table_ac


class ColumnId:
    def __init__( self, accession: str ):
        self.column_ac = accession
    
    
    def index( self, headers: List[ str ] ):
        if self.column_ac.startswith( "#" ):
            return int( self.column_ac[ 1: ] )
        
        for i, header in enumerate( headers ):
            if header == self.column_ac:
                return i
        
        raise KeyError( "The column '{}' cannot be found in any header: {}".format( self.column_ac, headers ) )
    
    
    def __str__( self ):
        return self.column_ac


class ColumnAndTableId:
    def __init__( self, accession: str ):
        if ":" in accession:
            table, column = accession.split( ":", 1 )
            self.table_id = TableId( table )
            self.column_id = ColumnId( column )
        else:
            self.table_id = TableId( current().accession )
            self.column_id = ColumnId( accession )
    
    
    def __str__( self ):
        return "{}:{}".format( self.table_id, self.column_id )


_files = { }
_top_file = Table()


def has_current():
    return _top_file is not None


def current() -> Table:
    if _top_file is None:
        raise ValueError( "You must load a table first." )
    
    return _top_file


def set_current( table: Table ):
    global _top_file
    _top_file = table


def all():
    return _files.values()


def get_file( accession: str ) -> Table:
    return _files[ accession ]


def new_table( accession: str ) -> Table:
    global _top_file
    
    f = Table()
    f.accession = accession
    _files[ accession ] = f
    _top_file = f
    return f


def close_file( accession: str ):
    global _top_file
    if _top_file.accession == accession:
        _top_file = None
    
    del _files[ accession ]
