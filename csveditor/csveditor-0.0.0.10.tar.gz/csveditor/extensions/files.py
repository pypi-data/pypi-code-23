import copy
from os import path
from typing import Optional

from colorama import Back, Fore, Style

from csveditor import tables
from csveditor.recent_files import RecentFilesList
from csveditor.tables import EQuote 
from intermake import MCMD, command, cli_helper, visibilities
from mhelper import array_helper, file_helper, string_helper, SwitchError, MEnum


@command( highlight = True )
def open( file_name: str, accession: Optional[ str ] = None ):
    """
    Opens a new table.
    
    :param file_name:   File to open. You can specify just the accession if the file appears in the recent-list.
    :param accession:   Accession to give the file. Leave this as `None` to just use the filename.
    :return: 
    """
    rfl = RecentFilesList()
    file_name = rfl.search( file_name )
    
    if accession is None:
        accession = file_helper.get_filename_without_extension( file_name ).lower()
    
    table = tables.new_table( accession.lower() )
    table.file_name = file_name
    table.load()
    
    rfl.append( table.accession, table.file_name )
    MCMD.information( "{}".format( table ) )
    MCMD.information( "{}".format( table.dialect ) )


@command()
def save_ext():
    """
    Same as the `save` command, but changes the filename between CSV or TSV to reflect the output delimiter.
    """
    table = tables.current()
    
    file_name = table.file_name
    
    dialect = table.out_dialect or table.dialect
    
    if dialect.delimiter == ",":
        file_name = file_helper.replace_extension( file_name, ".csv" )
    elif dialect.delimiter == "\t":
        file_name = file_helper.replace_extension( file_name, ".tsv" )
    else:
        raise ValueError( "Cannot use `save_ext` because this isn't a CSV or TSV file." )
    
    save( file_name )


@command( highlight = True )
def save( file_name: Optional[ str ] = None ):
    """
    Saves the current table.
    
    :param file_name:  Optional new filename to give the table.
    """
    
    table = tables.current()
    
    if file_name is None:
        file_name = table.file_name
    
    if not path.sep in file_name:
        raise ValueError( "Invalid '{}' filename. Please provide a full path.".format( file_name ) )
    
    if file_name is not None:
        table.file_name = file_name
    
    table.save()
    
    RecentFilesList().append( table.accession, table.file_name )
    MCMD.information( "Saved {}".format( table.file_name ) )


@command()
def switch( accession: str ):
    """
    Sets the active table.
    
    :param accession: Accession of the table (use `tables` to list).
    """
    tables.set_current( tables.get_file( accession ) )
    MCMD.print( "The current table is now '{}'".format( accession ) )


@command( names = ["tables"] )
def tables_():
    """
    Prints the tables.
    """
    if not array_helper.has_any( tables.all() ):
        MCMD.print( "No tables." )
    
    for table in tables.all():
        print_name( table.accession, table.file_name, table is tables.current() )


@command()
def recent():
    """
    Lists the recent files.
    """
    if not array_helper.has_any( RecentFilesList().items() ):
        MCMD.print( "No recent files." )
    
    for accession, file_name in RecentFilesList().items():
        print_name( accession, file_name, file_name in [ x.file_name for x in tables.all() ] )


def print_name( accession, file_name, highlight ):
    if highlight:
        prefix = Back.MAGENTA + Fore.LIGHTYELLOW_EX + string_helper.no_emoji("📂") + Style.RESET_ALL + " "
    else:
        prefix = ""
    
    MCMD.information( prefix + Fore.GREEN + accession + Fore.RESET + " "
                      + file_helper.suffix_directory( file_helper.get_directory( file_name ) )
                      + Fore.YELLOW + file_helper.get_filename_without_extension( file_name )
                      + Fore.RESET + file_helper.get_extension( file_name ) )


class EOut( MEnum ):
    """
    :data IN: Dialect used for reading
    :data OUT: Dialect used for writing. Note if this is not set the input dialect is used.
    """
    BOTH = 0
    IN = 1
    OUT = 2


# noinspection SpellCheckingInspection
@command( highlight = True )
def dialect( t: EOut = EOut.BOTH,
             delimiter: Optional[ str ] = None,
             quote: Optional[ str ] = None,
             escape: Optional[ str ] = None,
             double: Optional[ bool ] = None,
             skip: Optional[ bool ] = None,
             line: Optional[ str ] = None,
             quoting: Optional[ EQuote ] = None,
             header: Optional[ bool ] = None,
             trim: Optional[ bool ] = None,
             ):
    """
    Sets the CSV dialect.
    
    Remember, you can use string parameters such as `"\n"`.
    The following are also supported for convenience:
        `":n"`  - newline
        `":r"`  - carriage return
        `":t"`  - tab
        `":s"`  - space
        `":c"`  - comma
        `":l"`  - colon
        `":i"`  - semi-colon
        `":p"`  - pipe
        `":d"`  - double quote
        `":q"`  - single quote
    
    :param t:           Dialect to set.
    :param delimiter:   Delimiter character, e.g. `,`. 
    :param quote:       Quote character, e.g. `"` or `'`. 
    :param escape:      Escape character.
    :param double:      Escape quotes by doubling them (Excel-style). 
    :param skip:        Skip initial space. 
    :param line:        Newline character. 
    :param quoting:     Quoting mode. 
    :param header:      CSV has header?
    :param trim:        Trim all leading/trailing spaces from cells
    """
    table = tables.current()
    
    if t == EOut.BOTH:
        if table.out_dialect is not None:
            MCMD.information( "Input and output dialects have diverged. Please specify whether you wish to address the INput dialect or the OUTput dialect." )
            return
        
        MCMD.information( cli_helper.highlight_quotes( "Viewing input/output dialects - use `dialect IN` or `dialect OUT` to specify just one" ) )
        dn = "I/O DIALECT"
        d = table.dialect
    else:
        if table.out_dialect is None:
            table.out_dialect = copy.deepcopy( table.dialect )
        
        if t == EOut.IN:
            dn = "INPUT DIALECT"
            d = table.dialect
        elif t == EOut.OUT:
            dn = "OUTPUT DIALECT"
            d = table.out_dialect
        else:
            raise SwitchError( "t", t )
    
    ch = [ ]
    
    
    def __set_or_view( description, target, field, new_value, change_list ):
        if new_value is not None:
            if isinstance( new_value, str ):
                for s in ("n\n", "r\r", "t\t", "s ", "c,", "l:", "p|", 'd"', "q'"):
                    new_value = new_value.replace( ":" + s[ 0 ], s[ 1: ] )
            
            setattr( target, field, new_value )
            change_list.append( True )
        
        value = getattr( target, field )
        
        if isinstance( value, str ):
            value = Fore.CYAN + string_helper.special_to_symbol( value ) + Style.RESET_ALL
        elif isinstance( value, bool ):
            value = (Fore.GREEN + "✓" + Style.RESET_ALL) if value else (Fore.RED + "✗" + Style.RESET_ALL)
        else:
            value = Fore.MAGENTA + str( value ) + Style.RESET_ALL
        
        MCMD.information( description + str( value ) )
    
    
    MCMD.information( dn )
    __set_or_view( "Delimiter        : ", d, "delimiter", delimiter, ch )
    __set_or_view( "Quote character  : ", d, "quotechar", quote, ch )
    __set_or_view( "Escape character : ", d, "escapechar", escape, ch )
    __set_or_view( "Double quotes?   : ", d, "doublequote", double, ch )
    __set_or_view( "Skip space?      : ", d, "skipinitialspace", skip, ch )
    __set_or_view( "Line terminator  : ", d, "lineterminator", line, ch )
    __set_or_view( "Quote mode       : ", d, "quoting", quoting, ch )
    __set_or_view( "Header?          : ", d, "header", header, ch )
    __set_or_view( "Trim?            : ", d, "trim", trim, ch )
    
    table.place_header()


@command()
def close():
    """
    Closes the current table (without saving).
    :return: 
    """
    tables.close_file( tables.current().accession )
