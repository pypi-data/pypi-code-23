"""
Функции ​к​лиента:​
- сформировать ​​presence-сообщение;
- отправить ​с​ообщение ​с​ерверу;
- получить ​​ответ ​с​ервера;
- разобрать ​с​ообщение ​с​ервера;
- параметры ​к​омандной ​с​троки ​с​крипта ​c​lient.py ​​<addr> ​[​<port>]:
- addr ​-​ ​i​p-адрес ​с​ервера;
- port ​-​ ​t​cp-порт ​​на ​с​ервере, ​​по ​у​молчанию ​​7777.
"""
from queue import Queue
import logging
from socket import socket, AF_INET, SOCK_STREAM
from my_own_jim.config import *
from my_own_jim.utils import send_message, get_message
import my_own_logs.client_log_config
from my_own_logs.decorators import Log
from my_own_jim.core import JimPresence, JimMessage, Jim, JimResponse, JimDelContact, JimAddContact, JimContactList, \
    JimGetContacts

# Получаем по имени клиентский логгер, он уже нестроен в log_config
logger = logging.getLogger('client')
# создаем класс декоратор для логирования функций
log = Log(logger)


class User:
    def __init__(self, login, addr, port):
        self.addr = addr
        self.port = port
        self.login = login
        self.request_queue = Queue()

    def connect(self):
        # Соединиться с сервером
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.addr, self.port))
        # Создаем сообщение
        presence = self.create_presence()
        # Отсылаем сообщение
        send_message(self.sock, presence)
        # Получаем ответ
        response = get_message(self.sock)
        # Проверяем ответ
        response = self.translate_response(response)
        return response

    def disconnect(self):
        self.sock.close()

    @log
    def create_presence(self):
        """
        Сформировать ​​presence-сообщение
        :return: Словарь сообщения
        """
        # формируем сообщение
        jim_presence = JimPresence(self.login)
        message = jim_presence.to_dict()
        # возвращаем
        return message

    @log
    def translate_response(self, response):
        """
        Разбор сообщения
        :param response: Словарь ответа от сервера
        :return: корректный словарь ответа
        """
        result = Jim.from_dict(response)
        # возвращаем ответ
        return result.to_dict()

    def create_message(self, message_to, text):
        message = JimMessage(message_to, self.login, text)
        return message.to_dict()

    def get_contacts(self):
        # запрос на список контактов
        jimmessage = JimGetContacts(self.login)
        # отправляем
        send_message(self.sock, jimmessage.to_dict())
        # ответ получаем из очереди
        response = self.request_queue.get()
        # количество контактов
        quantity = response.quantity
        # имена читаем из очереди
        message = self.request_queue.get()
        # возвращаем список имен
        contacts = message.user_id
        return contacts

    def add_contact(self, username):
        # будем добавлять контакт
        message = JimAddContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ из очереди
        response = self.request_queue.get()
        return response

    def del_contact(self, username):
        # будем удалять контакт
        message = JimDelContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ из очереди
        response = self.request_queue.get()
        return response

    def send_message(self, to, text):
        # отправка сообщения
        message = JimMessage(to, self.login, text)
        # отправляем
        send_message(self.sock, message.to_dict())