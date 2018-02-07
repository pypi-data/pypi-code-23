import time
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread

from ...jim.core import *
from ...utils import start_thread, APP_PATH, get_full_path
from ..core import MyMessengerClient
from ..handlers import GuiReceiver
from .repo.models import session
from .repo.repo import Repo
from .utils import center
from .ui.MainWindow import Ui_MainWindow
from .dialogs import ConnectUI, AboutUI, ProfileUI


def get_icon(image):
    path = get_full_path(__file__, image)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return icon


class MyMessengerClientGUI(QtWidgets.QMainWindow):
    """GUI for MyMessenger"""
    def __init__(self, parent=None):
        super().__init__()
        # Client
        self.repo = Repo(session)
        self.ip = None
        self.port = None
        self.login = None
        self.password = None
        self.client = None
        self.listener = None
        self.client_thread = None
        self.listener_thread = None
        self.is_started = False
        # UI
        self.initUI()

    def initUI(self):
        """Prepare UI."""

        # Set window on screen center
        center(self)

        # Change runtime dir to correct work relative path in UI scripts.
        path = os.path.dirname(os.path.abspath(__file__))
        ui_files_path = os.path.join(path, 'ui')
        os.chdir(ui_files_path)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButtonChatSend.clicked.connect(self.chat_send)
        self.ui.pushButtonAddContact.clicked.connect(self.add_contact)
        self.ui.lineEditAddContact.returnPressed.connect(self.add_contact)
        self.ui.listWidgetContactList.itemDoubleClicked.connect(self.choose_room)
        self.ui.quit.triggered.connect(self.close)
        self.ui.about.triggered.connect(self.aboutDialog)
        self.ui.profile.triggered.connect(self.profileDialog)
        self.ui.pushButtonFormatB.clicked.connect(lambda: self.actionFormat('b'))
        self.ui.pushButtonFormatI.clicked.connect(lambda: self.actionFormat('i'))
        self.ui.pushButtonFormatU.clicked.connect(lambda: self.actionFormat('u'))
        self.ui.labelSmileBtn.mouseReleaseEvent = self.insertSmile

    def aboutDialog(self):
        """Launch Profile Window."""
        d = AboutUI(parent=self)
        d.exec()

    def profileDialog(self):
        """Launch About Window."""
        d = ProfileUI(parent=self)
        d.exec()

    def connect(self):
        """Open connect dialog modal window"""
        d = ConnectUI(parent=self)
        d.exec()

    def insertSmile(self, event):
        """Add smile to message."""
        url = os.path.join(APP_PATH, 'client/gui/img/smile/ab.gif')
        html = '<img src="{}" />'.format(url)
        self.ui.textEditChatInput.insertHtml(html)

    def closeEvent(self, event):
        """Extend of method. Activate stop methods of client and listener before close GUI."""
        if self.is_started:
            print('Waiting for threads finish... ', sep='')
            self.listener.stop()
            self.client.stop()
            self.client_thread.join()
            print('OK')
        else:
            print('Launch aborted')
        super().closeEvent(event)

    def start_listener(self):
        """Start GuiReceiver"""
        listener = GuiReceiver(self.client.socket, self.client.request_queue)
        listener.gotMessage.connect(self.update_chat)
        thread = QThread()
        listener.moveToThread(thread)
        thread.started.connect(listener.poll)
        thread.start()
        return listener, thread

    def actionFormat(self, tag):
        """Font format for text of messages to send."""
        text = self.ui.textEditChatInput.textCursor().selectedText()
        self.ui.textEditChatInput.textCursor().insertHtml('<{0}>{1}</{0}>'.format(tag, text))
        # self.ui.textEditChatInput.textCursor().insertText('<{0}>{1}</{0}>'.format(tag, text))

    def chat_send(self):
        """Send message."""
        msg_txt = self.ui.textEditChatInput.toHtml()
        # msg_txt = self.ui.textEditChatInput.toPlainText()
        jm = JimMessage(self.client.room, self.client.user.account_name, msg_txt)
        self.client.request(jm)
        self.ui.textEditChatInput.clear()
        text = '{} ({}):{}<br>'.format(self.login, time.strftime('%H:%M:%S'), msg_txt)
        self.ui.textEditChat.insertHtml(text)
        print(self.ui.textEditChat.toHtml())
        # self.ui.textEditChat.setHtml(text)

    def update_chat(self, msg):
        """Chat update."""
        try:
            print(msg)
            self.ui.textEditChat.textCursor().insertHtml('{}<br>'.format(msg))
        except Exception as e:
            print(e)

    def update_contact_list(self):
        """ContactWidget update."""
        try:
            self.ui.listWidgetContactList.clear()
            self.createContactItem('@all')
            for contact in self.client.get_contact_list():
                self.createContactItem(contact)
        except Exception as e:
            print(e)

    def createContactItem(self, contact):
        """Create item for Contact List"""
        item = QtWidgets.QListWidgetItem(self.ui.listWidgetContactList)
        widget = QtWidgets.QWidget()
        widgetText = QtWidgets.QLabel(contact)
        widgetButton = QtWidgets.QPushButton('X')
        widgetButton.setProperty('id', contact)
        widgetButton.clicked.connect(self.del_contact)
        widgetButton.setFixedWidth(31)
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.addWidget(widgetText)
        widgetLayout.addWidget(widgetButton)

        widget.setLayout(widgetLayout)
        item.setSizeHint(widget.sizeHint())
        self.ui.listWidgetContactList.setItemWidget(item, widget)

        item.setData(QtCore.Qt.UserRole, contact)

    def add_contact(self):
        """Add contact to contact list."""
        contact = self.ui.lineEditAddContact.text()
        self.ui.lineEditAddContact.clear()
        self.client.add_contact(contact)
        self.client.contact_list.append(contact)
        # self.ui.listWidgetContactList.addItem(contact)
        self.createContactItem(contact)

    def del_contact(self):
        """Remove contact from contact list."""
        widget = self.ui.listWidgetContactList
        contact = self.sender().property('id')
        self.client.del_contact(contact)
        index = self.client.contact_list.index(contact)
        widget.takeItem(index + 1)
        self.client.contact_list.remove(contact)

    def choose_room(self):
        """Change client.room"""
        item = self.ui.listWidgetContactList.currentItem() or self.ui.listWidgetContactList.item(0)
        room = item.data(QtCore.Qt.UserRole)
        self.client.room = room
        self.ui.groupBoxChatName.setTitle('Выбран чат: {}'.format(room))
        print('Room changed on: {}'.format(room))

    def run(self):
        """Start client."""
        self.connect()
        if not self.is_started:
            return True
        self.client = MyMessengerClient(self.login, self.password)
        self.client_thread = start_thread(self.client.run, 'Client', self.ip, self.port)
        while not self.client.is_alive:
            if not self.client_thread.is_alive():
                return False
        self.listener, self.listener_thread = self.start_listener()

        while not self.client.is_ready:
            time.sleep(0.1)
        self.client.contact_list_request()
        self.update_contact_list()
        self.choose_room()
        self.setWindowTitle('MyMessenger - {}'.format(self.login))

        return True
