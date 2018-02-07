import sys
import logging
import time
from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue

from ..jim.core import *
from ..jim.utils import send_message, get_message
from ..utils import start_thread, get_hash
from ..logger.config import logger_config
from ..logger.decorators import Log
from .errors import AuthenticateFail


logger_config('client', logging.DEBUG)
logger = logging.getLogger('client')
log = Log(logger)


class MyMessengerClient:
    """Клиент my_messenger."""

    def __init__(self, account_name, password):
        """Передаем имя пользователя и пароль."""
        self.user = JimUser(account_name, get_hash(password))
        self.socket = None
        self.room = None
        self.is_alive = False
        self.request_queue = Queue()
        self.contact_list = []
        self.is_contact_list_ready = False
        self.listener_parser_thread = None
        self.is_ready = False

    @log
    def presence(self):
        """Отправить приветствие серверу и обработать ответ."""
        print('Presence... ', end='')
        presence = JimPresence(self.user)
        self.request(presence)
        response = get_message(self.socket)
        response = Jim.from_dict(response).to_dict()
        if response['response'] == OK:
            print('OK')
            return True

    @log
    def authenticate(self):
        """Отправить запрос аутентификации и обработать ответ."""
        print('Authenticate... ')
        authenticate = JimAuthenticate(self.user)
        self.is_ready = True
        self.request(authenticate)
        response = get_message(self.socket)
        self.is_ready = True
        response = Jim.from_dict(response).to_dict()
        if response['response'] == ACCEPTED:
            print('ACCEPTED')
        else:
            print('FAIL')
            logger.warning('Authenticate FAILED')
            raise AuthenticateFail(response)

    @log
    def join_room(self, room):
        """Подключиться к комнате/чату."""
        self.room = room
        message = JimJoin(self.room)
        self.request(message)

    @log
    def leave_room(self):
        """Покупнить комнату/чат."""
        message = JimLeave(self.room)
        self.request(message)

    @log
    def add_contact(self, param):
        """Добавить контакт в список контактов."""
        message = JimAddContact(self.user.account_name, param)
        self.request(message)

    @log
    def del_contact(self, param):
        """Удалить контакт из списка контактов."""
        message = JimDelContact(self.user.account_name, param)
        self.request(message)

    @log
    def request(self, jm):
        """Отправить сообщение."""
        while not self.is_ready:
            time.sleep(0.1)
        self.is_ready = False
        try:
            send_message(self.socket, jm.to_dict())
        except:
            logger.exception('Request to server ERROR. {}'.format(jm.to_dict()))

    @log
    def response(self, response):
        """Обработка ответа от сервера."""
        self.is_ready = True
        if response.response in [OK, ACCEPTED]:
            pass
        elif response.error is not None:
            print(response.error)

    @log
    def contact_list_request(self, quantity=0):
        """Запросить список контактов."""
        if quantity == 0:
            self.contact_list = []
            self.is_contact_list_ready = False
        message = JimGetContacts(self.user.account_name, quantity)
        self.request(message)

    @log
    def contact_list_result(self, contact_list):
        """Обработка сообщения о контакте от сервера."""
        self.is_ready = True
        if contact_list.user_id != '':
            self.contact_list.append(contact_list.user_id)
        if contact_list.quantity > 0:
            self.contact_list_request(contact_list.quantity)
        else:
            self.is_contact_list_ready = True

    @log
    def get_contact_list(self):
        """Ждем загрузки списка контактов и возвращаем его."""
        while not self.is_contact_list_ready:
            time.sleep(0.1)
        return self.contact_list

    @log
    def listener_parser(self):
        """Обработка сообщений."""
        while self.is_alive:
            jm = self.request_queue.get()
            if isinstance(jm, JimResponse):
                self.response(jm)
            elif isinstance(jm, JimContactList):
                self.contact_list_result(jm)

    @log
    def stop(self):
        """Останов клиента."""
        self.is_alive = False
        self.request(JimQuit())

    @log
    def run(self, host, port):
        """Запуск клиента."""
        self.socket = socket(AF_INET, SOCK_STREAM)

        try:
            self.socket.connect((host, port))
        except ConnectionRefusedError:
            print('Connection Refused Error!')
            print('Check IP and port parameters.')
            return False

        try:
            self.authenticate()
        except AuthenticateFail as e:
            print(e)
            sys.exit()

        self.is_alive = True

        self.listener_parser_thread = start_thread(self.listener_parser, 'listener_parser')
        self.join_room(self.user.account_name)
        self.join_room('@all')

        self.listener_parser_thread.join()
