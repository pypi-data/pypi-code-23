import os
import sys
import time
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from .helpers import jim, console
from .client import Client

app = QApplication(sys.argv)
w = uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui/client.ui'))


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
        w.sendButton.clicked.connect(self.send_message)
        w.newContactButton.clicked.connect(self.add_contact)
        w.deleteContactButton.clicked.connect(self.delete_contact)
        w.newContactInput.returnPressed.connect(w.newContactButton.click)
        w.setWindowTitle('Echo ({})'.format(client.name))
        w.show()

        client.send(jim.Message(action='get_contacts'))

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
                w.messageInput.clear()

    def add_contact(self):
        contact_name = w.newContactInput.text()
        if contact_name:
            self.__client.send(jim.Message(action='add_contact', user_name=contact_name))
            time.sleep(0.2)
            w.contactList.clear()
            self.__client.send(jim.Message(action='get_contacts'))

    def delete_contact(self):
        selected_index = w.contactList.currentIndex()
        if selected_index:
            self.__client.send(jim.Message(action='del_contact', user_name=selected_index.data()))
            time.sleep(0.2)
            w.contactList.clear()
            self.__client.send(jim.Message(action='get_contacts'))


def run():
    console_params = console.args()
    cl = Client((console_params.address, console_params.port), console_params.user, receive_callback)
    if cl.connect():
        handler = Handler(cl)
        sys.exit(app.exec_())


if __name__ == "__main__":
    run()
