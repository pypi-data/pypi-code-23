import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication

import jim
from console import Params
from echo import client


def receive_callback(parcel):
    if parcel.action == 'contact_list':
        w.contactList.addItem(parcel.account_name)
    elif parcel.action == 'msg':
        w.chatArea.addItem('{}: {}'.format(parcel.sender, parcel.text))
    elif parcel.response == 400:
        w.chatArea.addItem('Error: {}'.format(parcel.error))


class Handler:
    def __init__(self, client):
        self.__client = client

    def send_message(self):
        text = w.messageInput.toPlainText()
        if text:
            params = {'action': 'msg', 'text': text}
            selected_index = w.contactList.currentIndex()
            if selected_index:
                user_name = selected_index.data()
                params['to'] = user_name
            if self.__client.send(jim.Message(**params)):
                w.chatArea.addItem('{}: {}'.format(self.__client.name, text))

    def add_contact(self):
        contact_name = w.newContactInput.text()
        if contact_name:
            w.contactList.clear()
            self.__client.send(jim.Message(action='add_contact', user_name=contact_name))
            self.__client.send(jim.Message(action='get_contacts'))


if __name__ == '__main__':
    console_params = Params(sys.argv)
    client = client.Client(console_params.console_host, console_params.account_name, receive_callback)
    if client.connect():

        app = QApplication(sys.argv)

        handler = Handler(client)
        w = uic.loadUi('src/ui/client.ui')
        w.sendButton.clicked.connect(handler.send_message)
        w.newContactButton.clicked.connect(handler.add_contact)
        w.show()

        client.send(jim.Message(action='get_contacts'))
        sys.exit(app.exec_())


