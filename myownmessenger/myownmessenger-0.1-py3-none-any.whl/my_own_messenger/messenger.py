from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSlot
import subprocess
import sys
import os



def main():
    window.show()
    # точка запуска приложения
    sys.exit(appl.exec_())
    # app.exec_()


def authentification():
    login = window.LoginPlainTextEdit.toPlainText()
    address = window.textEditServerAddress.toPlainText()

    # password = ui.PasswordPlainTextEdit.toPlainText()
    current_path_for_login = os.path.join(parent_dir_name, 'my_own_client/')
    if platform == 'win32':
        subprocess.Popen('python {}client_gui.py {} 7777 {}'.format(current_path_for_login, address, login), shell=True)
    else:
        subprocess.Popen('python3.6 {}client_gui.py {} 7777 {}'.format(current_path_for_login, address, login), shell=True)
    exit(0)
    return (login, password)



# Создаем приложение
# Для отображения изображений получаем текущую директорию
parent_dir_name = (os.path.dirname(os.path.realpath(__file__)) + '/')
current_path = os.path.join(parent_dir_name, 'my_own_client/ui_forms/')
app = QtWidgets.QApplication(sys.argv)
# грузим главную форму
window = uic.loadUi('{}login_page.ui'.format(current_path))

# Создаем приложение
platform = sys.platform
appl = QtWidgets.QApplication(sys.argv)
# Связываем кнопку и функцию аутентификации
window.pushButton.clicked.connect(authentification)


if __name__ == "__main__":
    main()