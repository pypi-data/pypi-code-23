import sys
from PyQt5 import QtWidgets

from .gui.main import MyMessengerClientGUI


def main():
    app = QtWidgets.QApplication(sys.argv)

    client_gui = MyMessengerClientGUI()
    while not client_gui.run():
        print('Run FAILED. Trying again...')
    if client_gui.is_started:
        client_gui.show()
        sys.exit(app.exec_())
    else:
        client_gui.close()


if __name__ == '__main__':
    main()
