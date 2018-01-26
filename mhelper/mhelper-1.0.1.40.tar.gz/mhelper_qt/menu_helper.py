from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMenu, QWidget


def show( control : QWidget, *args ) -> object:
    menu = QMenu()
    
    if control.window().styleSheet():
        menu.setStyleSheet(control.window().styleSheet())
        
    r = []
    
    for arg in args:
        r.append( menu.addAction( arg ) )
    
    selected = menu.exec_( control.mapToGlobal( QPoint( 0, control.height() ) ) )
    
    if selected is None:
        return None
    
    return args[r.index( selected )]
