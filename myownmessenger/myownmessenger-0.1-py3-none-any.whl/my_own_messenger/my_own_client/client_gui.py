import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QLabel,
    QAction, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon
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
# Для отображения изображений получаем текущую директорию
parent_dir_name = (os.path.dirname(os.path.realpath(__file__))+'/')
current_path = os.path.join(parent_dir_name, 'ui_forms/')
app = QtWidgets.QApplication(sys.argv)
# грузим главную форму
window = uic.loadUi('{}main.ui'.format(current_path))
""" Показать окно создания нового чата """
chat_dialog = uic.loadUi('{}new_chat.ui'.format(current_path))

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
        window.textEditChat.insertHtml('{}<br>'.format(msg))
        window.textEditHistory.insertHtml('{}<br>'.format(msg))
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
    text = window.textEditMessage.toHtml()
    if text:
        # получаем выделенного пользователя
        selected_index = window.listWidgetContacts.currentIndex()
        # получаем имя пользователя
        user_name = selected_index.data()
        # отправляем сообщение
        client.send_message(user_name, text)
        # будем выводить то что мы отправили в общем чате
        msg = 'You >>> {} : {}'.format(user_name, text)
        window.textEditChat.insertHtml('{}<br>'.format(msg))
        window.textEditHistory.insertHtml('{}<br>'.format(msg))
        window.textEditMessage.clear()


# связываем кнопку send с функцией отправки
window.PushButtonSend.clicked.connect(send_message)

def clean_workspace():
    """Очистка окна текущего чата"""
    # window.listWidgetMessages.clear()
    window.textEditChat.clear()


#При нажатии на имя контакта в списке контактов окно текущего чата очищается
window.listWidgetContacts.itemClicked.connect(clean_workspace)
#
# Удаление контакта из списка вызывается через контекстное меню
# При нажатии правой кнопкой мыши на контакте появляется кнопка Remove
window.listWidgetContacts.setContextMenuPolicy(Qt.CustomContextMenu)
window.listWidgetContacts.setContextMenuPolicy(Qt.ActionsContextMenu)
removeAction = QtWidgets.QAction("Remove", None)
removeAction.triggered.connect(del_contact)
window.listWidgetContacts.addAction(removeAction)


def change_avatar():
    """Изменение аватара"""
    fname = QFileDialog.getOpenFileName(window, 'Open file', '/home1')[0]
    pixmap = QPixmap(fname)
    window.labelAvatar.setPixmap(pixmap)


## Обновление аватара
window.labelAvatar.resize(80,80)
window.pushButtonChangeAvatar.clicked.connect(change_avatar)


def actionSmile():
    url = '{}ab.gif'.format(current_path)
    window.textEditMessage.insertHtml('<img src="%s" />' % url)


def actionMelancholy():
    url = '{}ac.gif'.format(current_path)
    window.textEditMessage.insertHtml('<img src="%s" />' % url)


def actionSurprise():
    url = '{}ai.gif'.format(current_path)
    window.textEditMessage.insertHtml('<img src="%s" />' % url)



# Связи кнопок смайлов с их использованием
window.pushButtonSmile.clicked.connect(actionSmile)
window.pushButtonMelancholy.clicked.connect(actionMelancholy)
window.pushButtonSurprise.clicked.connect(actionSurprise)


def actionFormat(tag):
    text = window.textEditMessage.textCursor().selectedText()
    window.textEditMessage.textCursor().insertHtml('<{0}>{1}</{0}>'.format(tag, text))

# Связи кнопок редактирования текста и их использованием
window.pushButtonBold.clicked.connect((lambda: actionFormat('b')))
window.pushButtonItalics.clicked.connect(lambda: actionFormat('i'))
window.pushButtonUnderline.clicked.connect(lambda: actionFormat('u'))


def chat_add_contact():
    try:
        """Добавление контакта в чат"""
        # получаем выбранный элемент в QListWidget
        current_item = chat_dialog.listWidgetYourContacts.currentItem()
        current_item = chat_dialog.listWidgetYourContacts.takeItem(chat_dialog.listWidgetYourContacts.row(current_item))
        chat_dialog.listWidgetChatList.addItem(current_item)
    except Exception as e:
        print(e)



def chat_remove_contact():
    try:
        """Удаление контакта из чата"""
        current_item = chat_dialog.listWidgetChatList.currentItem()
        current_item = chat_dialog.listWidgetChatList.takeItem(chat_dialog.listWidgetChatList.row(current_item))
        chat_dialog.listWidgetYourContacts.addItem(current_item)
    except Exception as e:
        print(e)



def show_newchat_dialog():
    # обнуляем списки диалога
    chat_dialog.listWidgetYourContacts.clear()
    chat_dialog.listWidgetChatList.clear()

    # добавляем контакты
    for contact in contact_list:
        chat_dialog.listWidgetYourContacts.addItem(contact)

    chat_dialog.exec_()


def make_chat():
    try:
        """Создание чата, пока не реализованно (создается просто клиент)"""
        chat_name = chat_dialog.textEditChatName.toPlainText()
        if chat_name:
            # добавляем контакт - шлем запрос на сервер ...
            client.add_contact(chat_name)
            # добавляем имя в QListWidget
            window.listWidgetContacts.addItem(chat_name)
    except Exception as e:
        print(e)

# Связи кнопок создания чата со слотами
window.pushButtonGroupChat.clicked.connect(show_newchat_dialog)
chat_dialog.pushButtonAdd.clicked.connect(chat_add_contact)
chat_dialog.pushButtonRemove.clicked.connect(chat_remove_contact)
chat_dialog.buttonBox.clicked.connect(chat_remove_contact)
chat_dialog.buttonBox.accepted.connect(make_chat)

# рисуем окно
window.show()
# точка запуска приложения
sys.exit(app.exec_())


