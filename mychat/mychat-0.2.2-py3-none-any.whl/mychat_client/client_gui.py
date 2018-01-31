import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSlot
from mychat_client.client import User
from mychat_client.handlers import GuiReceiver

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
    print(name)
except IndexError:
    login = input('Login: ')
    name = login

app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi('sv_main.ui')
client = User(name, addr, port)
client.connect()
listener = GuiReceiver(client.sock, client.request_queue)


@pyqtSlot(str)
def update_chat(data):
    try:
        msg = data
        window.listWidgetMessages.addItem(msg)
    except Exception as e:
        print(e)


listener.gotData.connect(update_chat)
th = QThread()
listener.moveToThread(th)

th.started.connect(listener.poll)
th.start()

contact_list = client.get_contacts()


def load_contacts(contacts):
    window.listWidgetContacts.clear()
    for contact in contacts:
        window.listWidgetContacts.addItem(contact)


load_contacts(contact_list)


def add_contact():
    try:
        username = window.textEditUsername.toPlainText()
        if username:
            client.add_contact(username)
            window.listWidgetContacts.addItem(username)
    except Exception as e:
        print(e)


window.pushButtonAddContact.clicked.connect(add_contact)


def del_contact():
    try:
        current_item = window.listWidgetContacts.currentItem()
        username = current_item.text()
        client.del_contact(username)
        current_item = window.listWidgetContactstake.Item(window.listWidgetContacts.row(current_item))
        del current_item
    except Exception as e:
        print(e)


def send_message():
    text = window.textEditMessage.toPlainText()
    if text:
        selected_index = window.listWidgetContacts.currentIndex()
        user_name = selected_index.data()
        client.send_message(user_name, text)
        msg = '{:>30}: {}'.format(name, text)
        window.listWidgetMessages.addItem(msg)
        window.textEditMessage.clear()


window.pushButtonDelContact.clicked.connect(del_contact)
window.pushButtonSend.clicked.connect(send_message)


# window.show()
# sys.exit(app.exec_())

def main():
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
