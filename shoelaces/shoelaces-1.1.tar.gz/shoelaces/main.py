import sys
import unittest
from shoelaces.mainwindow import *
#from testing import *
from PyQt5.QtWidgets import *


def cli():
    #pass

#if __name__ == '__main__':
    #unittest.main()
    if len(sys.argv) == 1:
        qApp = QApplication(sys.argv)
        qApp.setWindowIcon(QIcon(settings.appDir()+"/shoelaces/resources/logo.png"))
        aw = ApplicationWindow()
        aw.setWindowTitle("%s" % "Shoelaces")
        aw.show()
        sys.exit(qApp.exec_())


    else:
         #qApp = QCoreApplication(sys.argv)
         cla = commandLineApplication(sys.argv)


if __name__ == '__main__':
    cli()

