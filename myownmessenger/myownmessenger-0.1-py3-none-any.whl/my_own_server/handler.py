import logging
from my_own_jim.utils import send_message, get_message
from my_own_jim.config import *
from my_own_jim.core import Jim, JimMessage, JimResponse, JimContactList, JimAddContact, JimDelContact
from my_own_jim.exceptions import WrongInputError
from my_own_repo.server_models import session
from my_own_repo.server_repo import Repo
from my_own_repo.server_errors import ContactDoesNotExist

import my_own_logs.server_log_config
from my_own_logs.decorators import Log

# Получаем серверный логгер по имени, он уже объявлен в log_config и настроен
logger = logging.getLogger('server')
log = Log(logger)


class Handler:
    """Обработчик сообщений, тут будет основная логика сервера"""
    def __init__(self):
        # сохраняем репозиторий
        self.repo = Repo(session)

    def read_requests(self, r_clients, all_clients):
        """Чтение сообщений"""
        # Список входящих сообщений
        messages = []

        for sock in r_clients:
            try:
                # Получаем входящие сообщения
                message = get_message(sock)
                messages.append((message, sock))
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)

        # Возвращаем словарь сообщений
        return messages

    @log
    def write_responses(self, messages, names, all_clients):
        """Отправляем сообщения либо конкретному пользователю, либо тому, кто ждет ответа"""


        for message, sock in messages:
            try:
                # теперь нам приходят разные сообщения, будем их обрабатывать
                action = Jim.from_dict(message)
                if action.action == GET_CONTACTS:
                    # нам нужен репозиторий
                    contacts = self.repo.get_contacts(action.account_name)
                    # формируем ответ
                    response = JimResponse(ACCEPTED, quantity=len(contacts))
                    # Отправляем
                    send_message(sock, response.to_dict())
                    contact_names = [contact.Name for contact in contacts]
                    message = JimContactList(contact_names)
                    send_message(sock, message.to_dict())
                elif action.action == ADD_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.repo.add_contact(username, user_id)
                        # шлем удачный ответ
                        response = JimResponse(ACCEPTED)
                        # Отправляем
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        # формируем ошибку, такого контакта нет
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        # Отправляем
                        send_message(sock, response.to_dict())
                elif action.action == DEL_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.repo.del_contact(username, user_id)
                        # шлем удачный ответ
                        response = JimResponse(ACCEPTED)
                        # Отправляем
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        # формируем ошибку, такого контакта нет
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        # Отправляем
                        send_message(sock, response.to_dict())
                elif action.action == MSG:
                    # получаем кому надо отправить сообщение
                    to = action.to
                    # находим сокет этого клиента
                    client_sock = names[to]
                    # просто пересылаем туда сообщение
                    send_message(client_sock, action.to_dict())
            except WrongInputError as e:
                # Отправляем ошибку и текст из ошибки
                response = JimResponse(WRONG_REQUEST, error=str(e))
                send_message(sock, response.to_dict())
            except:  # Сокет недоступен, клиент отключился
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)

    @log
    def presence_response(self, presence_message):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Проверки
        try:
            presence = Jim.from_dict(presence_message)
            username = presence.account_name
            # сохраняем пользователя в базу если его там еще нет
            if not self.repo.client_exists(username):
                self.repo.add_client(username)
            # нам надо связать имя пользователя и сокет

        except Exception as e:
            # Шлем код ошибки
            response = JimResponse(WRONG_REQUEST, error=str(e))
            return response.to_dict(), None
        else:
            # Если всё хорошо шлем ОК
            response = JimResponse(OK)
            # возвращаем еще имя пользователя
            return response.to_dict(), username