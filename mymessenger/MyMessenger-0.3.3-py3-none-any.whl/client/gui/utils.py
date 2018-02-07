from PyQt5 import QtWidgets


def center(widget):
    screen = QtWidgets.QDesktopWidget().screenGeometry()
    size = widget.geometry()
    x = (screen.width() - size.width()) // 2
    y = (screen.height() - size.height()) // 2
    widget.move(x, y)
