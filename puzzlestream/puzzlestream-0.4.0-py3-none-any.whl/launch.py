from multiprocessing import current_process
from os import path
from time import sleep

if current_process().name == "MainProcess":
    import sys
    from PyQt5 import QtCore, QtGui, QtWidgets


def main():
    """ Create Application and MainWindow. """
    global app, psMainWindow

    app = QtWidgets.QApplication(sys.argv)
    currentDir = path.dirname(__file__)
    splash_pix = QtGui.QPixmap(
        path.join(currentDir, "./icons/PuzzleStream.png"))
    splash = QtWidgets.QSplashScreen(
        splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(
        QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splash.show()
    splash.showMessage("Launching PuzzleStream")

    from puzzlestream.ui.mainWindow import PSMainWindow
    psMainWindow = PSMainWindow()
    splash.finish(psMainWindow)
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
