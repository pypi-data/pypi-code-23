from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSlot
import subprocess
import sys
import os
import my_own_messenger.login_page as login_page




def main():
    # Связываем кнопку и функцию аутентификации
    ui.pushButton.clicked.connect(authentification)
    login_window.show()
    # точка запуска приложения
    sys.exit(appl.exec_())
    #app.exec_()


def authentification():
    login = ui.LoginPlainTextEdit.toPlainText()
    #password = ui.PasswordPlainTextEdit.toPlainText()
    current_path = os.path.join(parent_dir_name, 'my_own_client/')
    if platform == 'win32':
        subprocess.Popen('python {}client_gui.py localhost 7777 {}'.format(current_path, login), shell=True)
    else:
        subprocess.Popen('python3.6 {}client_gui.py localhost 7777 {}'.format(current_path, login), shell=True)
    exit(0)
    return (login, password)



if __name__ == "__main__":
    # Создаем приложение
    platform = sys.platform
    parent_dir_name = (os.path.dirname(os.path.realpath(__file__))+'/')
    print('PATH={}'.format(parent_dir_name))

    appl = QtWidgets.QApplication(sys.argv)
    # Запускаем форму аутентификаци
    login_window = QtWidgets.QMainWindow()
    ui = login_page.Ui_MainWindow()
    ui.setupUi(login_window)
    main()