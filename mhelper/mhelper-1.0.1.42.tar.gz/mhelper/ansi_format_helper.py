"""
Functions for formatting stuff using ANSI codes and/or esoteric UNICODE characters.
"""

from typing import Union, Iterable, cast

from colorama import Back, Fore, Style

from mhelper import ansi, ansi_helper, exception_helper, string_helper


def format_source( text: str,
                   keywords: Iterable[str],
                   variables: Iterable[str] ) -> str:
    """
    Prints source text, highlighting keywords and variables, and prefixing line numbers
    
    :param text:        Text to print
    :param keywords:    Keywords to highlight
    :param variables:   Variables to highlight
    :return:            Nothing
    """
    r = []
    
    text = text.split( "\n" )
    
    for i, line in enumerate( text ):
        prefix = Back.LIGHTBLACK_EX + Fore.BLACK + " " + str( i ).rjust( 4 ) + " " + Style.RESET_ALL + " "
        
        line = string_helper.highlight_words( line, keywords, Style.RESET_ALL + Fore.GREEN, Style.RESET_ALL )
        line = string_helper.highlight_words( line, variables, Style.RESET_ALL + Fore.CYAN, Style.RESET_ALL )
        
        r.append( prefix + line )
    
    return "\n".join( r )


def format_traceback( exception: Union[BaseException, str],
                      traceback_ = None,
                      warning = False,
                      wordwrap = 0 ) -> str:
    """
    Formats a traceback.
    
    :param exception:       Exception to display 
    :param traceback_:      Traceback text (leave as `None` to get the system traceback) 
    :param warning:         Set to `True` to use warning, rather than error, colours 
    :param wordwrap:        Set to the wordwrap width. 
    :return:                ANSI containing string  
    """
    output_list = []
    
    wordwrap = wordwrap or 140
    INTERIOR_WIDTH = wordwrap - 4
    
    if warning:
        ⅎMAIN = Style.RESET_ALL + Back.YELLOW + Fore.BLACK
        ⅎHIGH = Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.BLACK
        ⅎBORDER = Back.LIGHTYELLOW_EX + Fore.BLACK
        ⅎNORMAL = Fore.CYAN
        ⅎCODE = Fore.CYAN + Style.DIM
        ⅎLINE = Style.DIM + Fore.CYAN
        ⅎFILE = Fore.LIGHTCYAN_EX
    else:
        ⅎMAIN = Style.RESET_ALL + Back.WHITE + Fore.RED
        ⅎHIGH = Style.RESET_ALL + Back.WHITE + Fore.BLACK + ansi.ITALIC
        ⅎBORDER = Back.RED + Fore.WHITE
        ⅎNORMAL = Style.RESET_ALL + Back.WHITE + Fore.RED
        ⅎCODE = Style.RESET_ALL + Back.WHITE + Fore.BLACK
        ⅎLINE = Style.RESET_ALL + Back.WHITE + Fore.BLUE + ansi.DIM
        ⅎFILE = Style.RESET_ALL + Back.WHITE + Fore.BLUE
    
    S_V, S_TL, S_H, S_TR, S_VL, S_VR, S_BL, S_BR = "│┌─┐├┤└┘"
    
    LBORD = ⅎBORDER + S_V + ⅎMAIN + " "
    RBORD = ⅎMAIN + " " + ⅎBORDER + S_V + Style.RESET_ALL
    
    output_list.append( ⅎBORDER + S_TL + S_H * (wordwrap - 2) + S_TR + Style.RESET_ALL )
    
    if isinstance( exception, BaseException ):
        ex = exception
        
        while ex:
            if ex is not exception:
                output_list.append( LBORD + " ---CAUSED BY---".ljust( INTERIOR_WIDTH ) + RBORD )
            
            output_list.append( LBORD + ("⦂" + type( ex ).__name__ + "⦂").ljust( INTERIOR_WIDTH ) + RBORD )
            ex_text = ⅎMAIN + string_helper.highlight_quotes( str( ex ), "«", "»", ⅎHIGH, ⅎMAIN )
            
            for line in ansi_helper.wrap( ex_text, INTERIOR_WIDTH ):
                line = ansi_helper.ljust( line, INTERIOR_WIDTH )
                output_list.append( LBORD + line + RBORD )
                if len( output_list ) > 20:
                    output_list.append( LBORD + ansi_helper.ljust( "...(trunacated)...", INTERIOR_WIDTH ) + RBORD )
                    break
            
            ex = ex.__cause__
    
    else:
        output_list.append( LBORD + str( exception ).ljust( INTERIOR_WIDTH ) + RBORD )
    
    if not traceback_:
        traceback_ = exception_helper.full_traceback()
    
    lines = traceback_.split( "\n" )
    
    for i, line in enumerate( lines ):
        print_line = line.strip()
        
        if print_line.startswith( "File " ):
            print_line = ⅎLINE + string_helper.highlight_regex( print_line, "\\/([^\\/]*)\"", ⅎFILE, ⅎLINE )
            print_line = ⅎLINE + string_helper.highlight_regex( print_line, "line ([0-9]*),", ⅎFILE, ⅎLINE )
            print_line = ⅎLINE + string_helper.highlight_regex( print_line, "in (.*)$", ⅎCODE, ⅎLINE )
            print_line = ansi_helper.fix_width( print_line, INTERIOR_WIDTH )
            output_list.append( LBORD + print_line + RBORD )
        elif line.startswith( " " ):
            print_line = ansi_helper.fix_width( print_line, INTERIOR_WIDTH )
            output_list.append( LBORD + ansi_helper.fix_width( "    " + ⅎCODE + print_line, INTERIOR_WIDTH ) + RBORD )
        elif line.startswith( "*" ):
            c = wordwrap - len( print_line ) - 6
            output_list.append( ⅎBORDER + S_VL + cast( str, S_H * 4 ) + print_line + S_H * c + S_VR + Style.RESET_ALL )
        else:
            print_line = ansi_helper.fix_width( print_line, INTERIOR_WIDTH )
            output_list.append( LBORD + ⅎNORMAL + print_line + RBORD )
    
    output_list.append( ⅎBORDER + S_BL + S_H * (wordwrap - 2) + S_BR + Style.RESET_ALL )
    
    return "\n".join( output_list )


def format_two_columns( *,
                        left_margin: int,
                        centre_margin: int,
                        right_margin: int,
                        left_text: str,
                        right_text: str,
                        left_prefix: str = "",
                        right_prefix: str = "",
                        left_suffix: str = "",
                        right_suffix: str = "", ):
    """
    Formats a box.
    :param *: 
    :param left_margin:     Width of left margin 
    :param centre_margin:   Width of centre margin 
    :param right_margin:    Width of right margin 
    :param left_text:       Text in left column 
    :param right_text:      Text in right column 
    :param left_prefix:     Text added to left lines
    :param right_prefix:    Text added to right lines
    :param left_suffix:     Text added to left lines
    :param right_suffix:    Text added to right lines
    :return: 
    """
    r = []
    left_space = centre_margin - left_margin - 1
    right_space = right_margin - centre_margin
    
    left_lines = list( left_prefix + x + left_suffix for x in ansi_helper.wrap( left_text, left_space, pad = True ) )
    right_lines = list( right_prefix + x + right_suffix for x in ansi_helper.wrap( right_text, right_space ) )
    num_lines = max( len( left_lines ), len( right_lines ) )
    
    for i in range( num_lines ):
        left = left_lines[i] if i < len( left_lines ) else " " * left_space
        right = right_lines[i] if i < len( right_lines ) else " " * right_space
        
        text = (" " * left_margin) + left + Style.RESET_ALL + " " + right + Style.RESET_ALL
        r.append( text )
    
    return "\n".join( r )
