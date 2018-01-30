import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSlot
from client import User
from handlers import GuiReciever

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

# Создаем приложение
app = QtWidgets.QApplication(sys.argv)
# грузим главную форму
window = uic.loadUi('ui_forms/main.ui')
# создаем клиента на запись
client = User(name, addr, port)
# получаем список контактов с сервера, которые лежат у нас - не надежные
client.connect()
listener = GuiReciever(client.sock, client.request_queue)

@pyqtSlot(str)
def update_chat(data):
    """Отображение текущего чата"""
    try:
        msg = data
        window.listWidgetMessages.addItem(msg)
    except Exception as e:
        print(e)


def history():
    """Перенос текущего чата в окно истории"""
    try:
        c = str(window.listWidgetMessages.count())
        s = int(c)
        for i in range (0, s + 1):
            a = window.listWidgetMessages.takeItem(i)
            window.listWidgetHistory.addItem(a)
            a = window.listWidgetMessages.takeItem(i+1)
            window.listWidgetHistory.addItem(a)
    except Exception as e:
        print(e)
        

# сигнал мы берем из нашего GuiReciever
listener.gotData.connect(update_chat)
th = QThread()
listener.moveToThread(th)

# # ---------- Важная часть - связывание сигналов и слотов ----------
# При запуске потока будет вызван метод search_text
th.started.connect(listener.poll)
th.start()

contact_list = client.get_contacts()


def load_contacts(contacts):
    """Загрузка списка контактов"""
    # чистим список
    window.listWidgetContacts.clear()
    # добавляем
    for contact in contacts:
        window.listWidgetContacts.addItem(contact)


# грузим контакты в список сразу при запуске приложения
load_contacts(contact_list)


def add_contact():
    """Добавление контакта"""
    # Получаем имя из QTextEdit
    try:
        username = window.textEditUsername.toPlainText()
        if username:
            # добавляем контакт - шлем запрос на сервер ...
            client.add_contact(username)
            # добавляем имя в QListWidget
            window.listWidgetContacts.addItem(username)
    except Exception as e:
        print(e)


# Связываем сигнал нажатия кнопки добавить со слотом функцией добавить контакт
window.pushButtonAddContact.clicked.connect(add_contact)


def del_contact():
    try:
        """Удаление контакта"""
        # получаем выбранный элемент в QListWidget
        current_item = window.listWidgetContacts.currentItem()
        # получаем текст - это имя нашего контакта
        username = current_item.text()
        # удаление контакта (отправляем запрос на сервер)
        client.del_contact(username)
        # удаляем контакт из QListWidget
        current_item = window.listWidgetContacts.takeItem(window.listWidgetContacts.row(current_item))
        del current_item
    except Exception as e:
        print(e)


def send_message():
    """Отправка сообщения"""
    text = window.textEditMessage.toPlainText()
    if text:
        # получаем выделенного пользователя
        selected_index = window.listWidgetContacts.currentIndex()
        # получаем имя пользователя
        user_name = selected_index.data()
        # отправляем сообщение
        client.send_message(user_name, text)
        # будем выводить то что мы отправили в общем чате
        msg = 'You >>> {} : {}'.format(user_name, text)
        window.listWidgetMessages.addItem(msg)
        window.textEditMessage.clear()


# связываем кнопку send с функцией отправки
window.PushButtonSend.clicked.connect(send_message)

def clean_workspace():
    """Очистка окна текущего чата"""
    history()
    window.listWidgetMessages.clear()


# При нажатии на имя контакта в списке контактов сообщения из окна текущего чата переносятся в окно history
window.listWidgetContacts.itemClicked.connect(clean_workspace)

# Удаление контакта из списка вызывается через контекстное меню
# При нажатии правой кнопкой мыши на контакте появляется кнопка Remove
window.listWidgetContacts.setContextMenuPolicy(Qt.CustomContextMenu)
window.listWidgetContacts.setContextMenuPolicy(Qt.ActionsContextMenu)
removeAction = QtWidgets.QAction("Remove", None)
removeAction.triggered.connect(del_contact)
window.listWidgetContacts.addAction(removeAction)




# рисуем окно
window.show()
# точка запуска приложения
sys.exit(app.exec_())


