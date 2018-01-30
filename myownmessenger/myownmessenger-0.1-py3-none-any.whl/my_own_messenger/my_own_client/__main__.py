import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSlot
import my_own_client.client_view as client_view
from my_own_client.client import User
from my_own_client.handlers import GuiReciever


def main():
    

    # сигнал мы берем из нашего GuiReciever
    listener.gotData.connect(update_chat)
    th = QThread()
    listener.moveToThread(th)

    # # ---------- Важная часть - связывание сигналов и слотов ----------
    # При запуске потока будет вызван метод search_text
    th.started.connect(listener.poll)
    th.start()

    contact_list = client.get_contacts()

    # грузим контакты в список сразу при запуске приложения
    load_contacts(contact_list)

    # Связываем сигнал нажатия кнопки добавить со слотом функцией добавить контакт
    ui.pushButtonAddContact.clicked.connect(add_contact)

    # связываем кнопку send с функцией отправки
    ui.PushButtonSend.clicked.connect(send_message)

    # При нажатии на имя контакта в списке контактов сообщения из окна текущего чата переносятся в окно history
    ui.listWidgetContacts.itemClicked.connect(clean_workspace)

    # Удаление контакта из списка вызывается через контекстное меню
    # При нажатии правой кнопкой мыши на контакте появляется кнопка Remove
    ui.listWidgetContacts.setContextMenuPolicy(Qt.CustomContextMenu)
    ui.listWidgetContacts.setContextMenuPolicy(Qt.ActionsContextMenu)
    removeAction = QtWidgets.QAction("Remove", None)
    removeAction.triggered.connect(del_contact)
    ui.listWidgetContacts.addAction(removeAction)

    # рисуем окно
    window.show()
    # точка запуска приложения
    sys.exit(app.exec_())


    


@pyqtSlot(str)
def update_chat(data):
    """Отображение текущего чата"""
    try:
        msg = data
        ui.listWidgetMessages.addItem(msg)
    except Exception as e:
        print(e)


def history():
    """Перенос текущего чата в окно истории"""
    try:
        c = str(ui.listWidgetMessages.count())
        s = int(c)
        for i in range (0, s + 1):
            a = ui.listWidgetMessages.takeItem(i)
            ui.listWidgetHistory.addItem(a)
            a = ui.listWidgetMessages.takeItem(i+1)
            ui.listWidgetHistory.addItem(a)
    except Exception as e:
        print(e)
        

def load_contacts(contacts):
    """Загрузка списка контактов"""
    # чистим список
    ui.listWidgetContacts.clear()
    # добавляем
    for contact in contacts:
        ui.listWidgetContacts.addItem(contact)


def add_contact():
    """Добавление контакта"""
    # Получаем имя из QTextEdit
    try:
        username = ui.textEditUsername.toPlainText()
        if username:
            # добавляем контакт - шлем запрос на сервер ...
            client.add_contact(username)
            # добавляем имя в QListWidget
            ui.listWidgetContacts.addItem(username)
    except Exception as e:
        print(e)





def del_contact():
    try:
        """Удаление контакта"""
        # получаем выбранный элемент в QListWidget
        current_item = ui.listWidgetContacts.currentItem()
        # получаем текст - это имя нашего контакта
        username = current_item.text()
        # удаление контакта (отправляем запрос на сервер)
        client.del_contact(username)
        # удаляем контакт из QListWidget
        current_item = ui.listWidgetContacts.takeItem(ui.listWidgetContacts.row(current_item))
        del current_item
    except Exception as e:
        print(e)


def send_message():
    """Отправка сообщения"""
    text = ui.textEditMessage.toPlainText()
    if text:
        # получаем выделенного пользователя
        selected_index = ui.listWidgetContacts.currentIndex()
        # получаем имя пользователя
        user_name = selected_index.data()
        # отправляем сообщение
        client.send_message(user_name, text)
        # будем выводить то что мы отправили в общем чате
        msg = 'You >>> {} : {}'.format(user_name, text)
        ui.listWidgetMessages.addItem(msg)
        ui.textEditMessage.clear()



def clean_workspace():
    """Очистка окна текущего чата"""
    history()
    ui.listWidgetMessages.clear()



if __name__ == "__main__":
        # Получаем параметры скрипта
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = 'localhost'
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)
    try:
        name = sys.argv[3]
    except IndexError:
        name = 'Guest'
        for params in sys.argv:
            print(params)

        # создаем клиента на запись
    client = User(name, addr, port)
    # получаем список контактов с сервера, которые лежат у нас - не надежные
    client.connect()
    listener = GuiReciever(client.sock, client.request_queue)
    # Создаем приложение
    app = QtWidgets.QApplication(sys.argv)
    # грузим главную форму
    window = QtWidgets.QMainWindow()
    ui = client_view.Ui_MainWindow()
    ui.setupUi(window)
    main()



