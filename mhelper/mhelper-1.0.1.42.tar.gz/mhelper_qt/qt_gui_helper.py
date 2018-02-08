import traceback
import functools
from typing import Optional, Dict

from PyQt5.QtWidgets import QLineEdit

from mhelper import string_helper, ImplementationError, ansi
from mhelper.generics_helper import DECORATOR_FUNCTION, DECORATOR, DECORATED


def exceptToGui() -> DECORATOR_FUNCTION:
    """
    DECORATOR
    
    Same as `exqtSlot` but without the `pyqtSlot` bit.
    """
    
    
    def true_decorator( fn ) -> DECORATOR:
        @functools.wraps( fn )
        def fn_wrapper( *args, **kwargs ) -> DECORATED:
            try:
                return fn( *args, **kwargs )
            except Exception as ex:
                show_exception( args[0], "Error", ex )
        
        
        # noinspection PyTypeChecker
        return fn_wrapper
    
    
    return true_decorator


def exqtSlot( *decorator_args ) -> DECORATOR_FUNCTION:
    """
    DECORATOR
    
    `pyqtSlot` is problematic in that if an exception occurs the application will silently exit.
    This decorator replaces `pyqtSlot` by adding not only the decorator, but a simple error handler. 
    """
    
    
    def true_decorator( fn ) -> DECORATOR:
        from PyQt5.QtCore import pyqtSlot
        return pyqtSlot( *decorator_args )( exceptToGui()( fn ) )
    
    
    return true_decorator


def browse_dir_on_textbox( textbox ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    :type textbox: QLineEdit
    """
    owner = textbox.window()
    
    from PyQt5.QtWidgets import QFileDialog
    dir_name = str( QFileDialog.getExistingDirectory( owner, "Select directory", textbox.text(), QFileDialog.DontUseNativeDialog ) )
    
    if not dir_name:
        return False
    
    textbox.setText( dir_name )
    
    return True


def browse_dir( owner, existing = None ):
    from PyQt5.QtWidgets import QFileDialog
    return str( QFileDialog.getExistingDirectory( owner, "Select directory", existing, QFileDialog.DontUseNativeDialog ) )


def browse_open_on_textbox( textbox:QLineEdit ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    """
    from mhelper import file_helper
    
    owner = textbox.window()
    directory = file_helper.get_directory( textbox.text() )
    
    from PyQt5.QtWidgets import QFileDialog
    dir_name = str( QFileDialog.getOpenFileName( owner, "Select file", directory ) )
    
    if not dir_name:
        return False
    
    textbox.setText( dir_name )
    
    return True

def browse_save_on_textbox( textbox:QLineEdit, filter ) -> bool:
    """
    Opens a file browser, using a textbox to retrieve and store the filename.
    """
    from mhelper import file_helper
    
    owner = textbox.window()
    directory = file_helper.get_directory( textbox.text() )
    
    from PyQt5.QtWidgets import QFileDialog
    dir_name = str( QFileDialog.getSaveFileName( owner, "Select file", directory, filter, options = QFileDialog.DontUseNativeDialog ) )
    
    if not dir_name:
        return False
    
    textbox.setText( dir_name )
    
    return True


def browse_save( parent, filter ):
    from mhelper import file_helper
    
    from PyQt5.QtWidgets import QFileDialog
    file_name, file_filter = QFileDialog.getSaveFileName( parent, "Save", "", filter, options = QFileDialog.DontUseNativeDialog )
    
    if file_name:
        if not file_helper.get_extension( file_name ):
            file_filter = get_extension_from_filter( file_filter )
            
            file_name += file_filter
    
    return file_name or None


def browse_open( parent, filter ):
    from PyQt5.QtWidgets import QFileDialog
    file_name, file_filter = QFileDialog.getOpenFileName( parent, "Open", "", filter, options = QFileDialog.DontUseNativeDialog )
    
    return file_name or None


def get_extension_from_filter( file_filter ):
    """
    Gets the first extension from a filter of the form
    
    Data ( *.txt ) --> .txt
    Data (*.txt) --> .txt
    Data (*.txt, *.csv) --> .txt
    Data (*.txt *.csv) --> .txt
    etc.
    """
    file_filter = file_filter.split( "(", 1 )[1].strip( " *" )
    
    for x in " ,)":
        if x in file_filter:
            file_filter = file_filter.split( x, 1 )[0]
    return file_filter


# noinspection PyUnusedLocal
def show_exception( owner, message = None, exception = None, traceback_ = None ) -> None:
    if not traceback_:
        traceback_ = traceback.format_exc()
    
    if isinstance( message, BaseException ):
        exception = message
        message = "Error"
    
    from PyQt5.QtWidgets import QMessageBox
    msg = QMessageBox()
    msg.setIcon( QMessageBox.Critical )
    msg.setText( str( message ) )
    
    if isinstance( exception, BaseException ):
        print( "{}: {}".format( type( exception ).__name__, exception ) )
        print( traceback_ )
        msg.setInformativeText( str( exception ) )
        msg.setDetailedText( traceback_ )
        
        msg.exec_()


def to_check_state( value ):
    from PyQt5.QtCore import Qt
    if value is None:
        return Qt.PartiallyChecked
    elif value:
        return Qt.Checked
    else:
        return Qt.Unchecked


def from_check_state( value ):
    from PyQt5.QtCore import Qt
    if value == Qt.PartiallyChecked:
        return None
    elif value == Qt.Checked:
        return True
    elif value == Qt.Unchecked:
        return False
    else:
        from mhelper.exception_helper import SwitchError
        raise SwitchError( "from_check_state.value", value )


def move_treeview_items( source, destination, only_selected = True ):
    from PyQt5.QtWidgets import QTreeWidget
    assert isinstance( source, QTreeWidget )
    assert isinstance( destination, QTreeWidget )
    
    if only_selected:
        selected_items = source.selectedItems()
    else:
        selected_items = []
        
        for index in range( source.topLevelItemCount() ):
            selected_items.append( source.topLevelItem( index ) )
    
    for item in selected_items:
        index = source.indexOfTopLevelItem( item )
        source.takeTopLevelItem( index )
        destination.addTopLevelItem( item )


class AnsiHtmlLine:
    def __init__( self, code, back = None, fore = None, style = None, family = None ):
        """
        CONSTRUCTOR
        :param code:            ANSI code 
        :param back:            Back colour 
        :param fore:            Fore colour 
        :param style:           Font style 
        :param family:          Font family 
        """
        if isinstance( code, AnsiHtmlLine ):
            self.code = code.code
            self.back = code.back
            self.fore = code.fore
            self.style = code.style
            self.family = code.family
        else:
            self.code = code
            self.back = back
            self.fore = fore
            self.style = style
            self.family = family
    
    
    def to_style( self ):
        return 'background:{}; color:{}; font-style:{}; font-family:{}'.format( self.back, self.fore, self.style, self.family )
    
    
    def copy( self ):
        return AnsiHtmlLine( self.code, self.back, self.fore, self.style, self.family )


class AnsiHtmlScheme:
    def __init__( self, values ):
        values = [x if isinstance( x, AnsiHtmlLine ) else AnsiHtmlLine( *x ) for x in values]
        self.values: Dict[int, AnsiHtmlLine] = dict( (x.code, x) for x in values )
    
    
    def copy( self ) -> "AnsiHtmlScheme":
        return AnsiHtmlScheme( (x.copy() for x in self.values.values()) )
    
    
    def __getitem__( self, item: int ) -> AnsiHtmlLine:
        return self.values[item]
    
    
    def get_default( self ) -> AnsiHtmlLine:
        return self[ansi.CODE_INTERNAL_DEFAULT]


def ansi_scheme_dark( fg = "#FFFFFF", bg = "#000000", style = "normal", family = "sans-serif" ) -> AnsiHtmlScheme:
    """
    Creates a new ANSI scheme, defaulted to dark values.
    """
    return AnsiHtmlScheme( ((ansi.CODE_FORE_BLACK, "", "#000000", "", ""),
                            (ansi.CODE_FORE_RED, "", "#FF0000", "", ""),
                            (ansi.CODE_FORE_GREEN, "", "#00FF00", "", ""),
                            (ansi.CODE_FORE_YELLOW, "", "#FFFF00", "", ""),
                            (ansi.CODE_FORE_BLUE, "", "#0000FF", "", ""),
                            (ansi.CODE_FORE_MAGENTA, "", "#FF00FF", "", ""),
                            (ansi.CODE_FORE_CYAN, "", "#00FFFF", "", ""),
                            (ansi.CODE_FORE_WHITE, "", "#FFFFFF", "", ""),
                            (ansi.CODE_FORE_RESET, "", "*", "", ""),
                            (ansi.CODE_FORE_LIGHT_BLACK, "", "#808080", "", ""),
                            (ansi.CODE_FORE_LIGHT_RED, "", "#FF8080", "", ""),
                            (ansi.CODE_FORE_LIGHT_GREEN, "", "#80FF80", "", ""),
                            (ansi.CODE_FORE_LIGHT_YELLOW, "", "#FFFF80", "", ""),
                            (ansi.CODE_FORE_LIGHT_BLUE, "", "#8080FF", "", ""),
                            (ansi.CODE_FORE_LIGHT_MAGENTA, "", "#FF80FF", "", ""),
                            (ansi.CODE_FORE_LIGHT_CYAN, "", "#80FFFF", "", ""),
                            (ansi.CODE_FORE_LIGHT_WHITE, "", "#FFFFFF", "", ""),
                            (ansi.CODE_BACK_BLACK, "#000000", "", "", ""),
                            (ansi.CODE_BACK_RED, "#FF0000", "", "", ""),
                            (ansi.CODE_BACK_GREEN, "#00FF00", "", "", ""),
                            (ansi.CODE_BACK_YELLOW, "#FFFF00", "", "", ""),
                            (ansi.CODE_BACK_BLUE, "#0000FF", "", "", ""),
                            (ansi.CODE_BACK_MAGENTA, "#FF00FF", "", "", ""),
                            (ansi.CODE_BACK_CYAN, "#00FFFF", "", "", ""),
                            (ansi.CODE_BACK_WHITE, "#FFFFFF", "", "", ""),
                            (ansi.CODE_BACK_RESET, "*", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_BLACK, "#808080", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_RED, "#FF8080", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_GREEN, "#80FF80", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_YELLOW, "#FFFF80", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_BLUE, "#8080FF", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_MAGENTA, "#FF80FF", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_CYAN, "#80FFFF", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_WHITE, "#FFFFFF", "", "", ""),
                            (ansi.CODE_STYLE_RESET_ALL, "*", "*", "*", ""),
                            (ansi.CODE_STYLE_BRIGHT, "", "", "bold", ""),
                            (ansi.CODE_STYLE_DIM, "", "", "italic", ""),
                            (ansi.CODE_STYLE_NORMAL, "", "", "normal", ""),
                            (ansi.CODE_INTERNAL_DEFAULT, bg, fg, style, family),
                            (ansi.CODE_INTERNAL_QUOTE_START, "", "#00C0FF", "", "monospace"),
                            (ansi.CODE_INTERNAL_QUOTE_END, "", "*", "", "*"),
                            (ansi.CODE_INTERNAL_TABLE_START, "", "", "", "monospace"),
                            (ansi.CODE_INTERNAL_TABLE_END, "", "", "", "*"),
                            ) )


def ansi_scheme_light( fg = "#000000", bg = "#FFFFFF" ) -> AnsiHtmlScheme:
    """
    Creates a new ANSI scheme, defaulted to light values.
    """
    return AnsiHtmlScheme( ((ansi.CODE_FORE_BLACK, "", "#000000", "", ""),
                            (ansi.CODE_FORE_RED, "", "#C00000", "", ""),
                            (ansi.CODE_FORE_GREEN, "", "#00C000", "", ""),
                            (ansi.CODE_FORE_YELLOW, "", "#C0C000", "", ""),
                            (ansi.CODE_FORE_BLUE, "", "#0000C0", "", ""),
                            (ansi.CODE_FORE_MAGENTA, "", "#C000C0", "", ""),
                            (ansi.CODE_FORE_CYAN, "", "#00C0C0", "", ""),
                            (ansi.CODE_FORE_WHITE, "", "#C0C0C0", "", ""),
                            (ansi.CODE_FORE_RESET, "", "*", "", ""),
                            (ansi.CODE_FORE_LIGHT_BLACK, "", "#C0C0C0", "", ""),
                            (ansi.CODE_FORE_LIGHT_RED, "", "#FF0000", "", ""),
                            (ansi.CODE_FORE_LIGHT_GREEN, "", "#00FF00", "", ""),
                            (ansi.CODE_FORE_LIGHT_YELLOW, "", "#FFFF00", "", ""),
                            (ansi.CODE_FORE_LIGHT_BLUE, "", "#0000FF", "", ""),
                            (ansi.CODE_FORE_LIGHT_MAGENTA, "", "#FF00FF", "", ""),
                            (ansi.CODE_FORE_LIGHT_CYAN, "", "#00FFFF", "", ""),
                            (ansi.CODE_FORE_LIGHT_WHITE, "", "#FFFFFF", "", ""),
                            (ansi.CODE_BACK_BLACK, "#000000", "", "", ""),
                            (ansi.CODE_BACK_RED, "#C00000", "", "", ""),
                            (ansi.CODE_BACK_GREEN, "#00C000", "", "", ""),
                            (ansi.CODE_BACK_YELLOW, "#C0C000", "", "", ""),
                            (ansi.CODE_BACK_BLUE, "#0000C0", "", "", ""),
                            (ansi.CODE_BACK_MAGENTA, "#C000C0", "", "", ""),
                            (ansi.CODE_BACK_CYAN, "#00C0C0", "", "", ""),
                            (ansi.CODE_BACK_WHITE, "#C0C0C0", "", "", ""),
                            (ansi.CODE_BACK_RESET, "*", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_BLACK, "#C0C0C0", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_RED, "#FF0000", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_GREEN, "#00FF00", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_YELLOW, "#FFFF00", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_BLUE, "#0000FF", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_MAGENTA, "#FF00FF", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_CYAN, "#00FFFF", "", "", ""),
                            (ansi.CODE_BACK_LIGHT_WHITE, "#FFFFFF", "", "", ""),
                            (ansi.CODE_STYLE_RESET_ALL, "*", "*", "*", ""),
                            (ansi.CODE_STYLE_BRIGHT, "", "", "bold", ""),
                            (ansi.CODE_STYLE_DIM, "", "", "italic", ""),
                            (ansi.CODE_STYLE_NORMAL, "", "", "normal", ""),
                            (ansi.CODE_INTERNAL_DEFAULT, bg, fg, "normal", "sans-serif"),
                            (ansi.CODE_INTERNAL_QUOTE_START, "", "#0080C0", "", "Consolas, monospace"),
                            (ansi.CODE_INTERNAL_QUOTE_END, "", "*", "", "*"),
                            (ansi.CODE_INTERNAL_TABLE_START, "", "", "", "Consolas, monospace"),
                            (ansi.CODE_INTERNAL_TABLE_END, "", "", "", "*")
                            ) )


def ansi_to_html( text: Optional[str], lookup: Optional[AnsiHtmlScheme] = None, *, debug: bool = False ) -> str:
    """
    Converts ANSI text to HTML.
    
    :param text:            Text to convert 
    :param lookup:          An `AnsiHtmlScheme` object defining the colours to use, or `None` for the default (dark).
                            See functions `ansi_scheme_dark` and `ansi_scheme_light`. 
    :param debug:           When `True`, prints the results to a temporary file. 
    :return:                The HTML. 
    """
    if text is None:
        return ""
    
    from mhelper.string_parser import StringParser
    html = []
    
    lookup = lookup.values if lookup is not None else ansi_scheme_dark().values
    default_style = lookup[ansi.CODE_INTERNAL_DEFAULT]
    current_style = AnsiHtmlLine( default_style )
    
    text = string_helper.highlight_quotes( text, "`", "`", "\033[-2m", "\033[-3m" )
    text = string_helper.highlight_quotes( text, "┌", "┘", "\033[-4m", "\033[-5m" )
    text = string_helper.highlight_quotes( text, "«", "»", "\033[-2m", "\033[-3m" )
    
    text = text.replace( "\n* ", "\n• " )
    text = text.replace( "\n", '<br/>' )
    text = text.replace( " ", ' ' )
    
    parser = StringParser( text )
    
    html.append( '<span style="background:{}; color:{}; font-style:{}; font-family:{};">'.format( current_style.back, current_style.fore, current_style.style, current_style.family ) )
    iterations = 0
    
    ANSI_ESCAPE = '\033['
    
    while not parser.end():
        iterations += 1
        
        if iterations >= 10000:
            raise ImplementationError( "Possible infinite loop in mhelper.qt_gui_helper.ansi_to_html. Internal error. Possible solutions: Use a shorter string. Check the lookup syntax." )
        
        html.append( parser.read_past( ANSI_ESCAPE ) )
        
        if parser.end():
            break
        
        code_str = parser.read_past( "m" )
        
        try:
            code = int( code_str )
        except:
            code = None
        
        if code is not None:
            new_style = lookup[code]
            
            for attr in "fore", "back", "family", "style":
                new = getattr( new_style, attr )
                if new:
                    if new == "*":
                        setattr( current_style, attr, getattr( default_style, attr ) )
                    else:
                        setattr( current_style, attr, new )
            
            html.append( '<span style="{}">'.format( current_style.to_style() ) )
    
    html.append( '</span>' )
    
    result = "".join( html )
    
    if debug:
        txx = ["ANSI", text, "HTML", result]
        from mhelper import file_helper
        file_helper.write_all_text( "temp-del-me.txt", "\n".join( txx ) )
    
    return result


__author__ = "Martin Rusilowicz"


class QtMutex:
    """
    A `QMutex` wrapped in Python.
    
    This is a `QMutex` and requires QT.
    - It is only for the GUI!
    - - Plugins should *not* use this!
    
    Usage:

        ```
        m = QtMutex()
        
        with m:
           . . .
           
        ```
           
    """
    
    
    def __init__( self ):
        from PyQt5.QtCore import QMutex
        self._mutex = QMutex()
    
    
    def __enter__( self ):
        self._mutex.lock()
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        self._mutex.unlock()


def suppress_debugging():
    # Disable PyQT logging to console since we use console for other stuff, plus, it's irritating
    # noinspection PyUnusedLocal
    def __message_handler( msg_type, msg_log_context, msg_string ):
        pass
    
    
    from PyQt5 import QtCore
    QtCore.qInstallMessageHandler( __message_handler )
