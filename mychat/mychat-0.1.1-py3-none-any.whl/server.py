"""
Функции ​​сервера:​
- принимает ​с​ообщение ​к​лиента;
- формирует ​​ответ ​к​лиенту;
- отправляет ​​ответ ​к​лиенту;
- имеет ​​параметры ​к​омандной ​с​троки:
- -p ​​<port> ​-​ ​​TCP-порт ​​для ​​работы ​(​по ​у​молчанию ​​использует ​​порт ​​7777);
- -a ​​<addr> ​-​ ​I​P-адрес ​​для ​​прослушивания ​(​по ​у​молчанию ​с​лушает ​​все ​​доступные ​​адреса).
"""
import sys
import logging
import select
from socket import socket, AF_INET, SOCK_STREAM
from Tschat_repo.server_models import session
from Tschat_repo.server_repo import Repo
from Tschat_repo.server_errors import ContactDoesNotExist
from Tschat_jim.utils import get_message, send_message
from Tschat_jim.config import *
from Tschat_jim.core import Jim, JimMessage, JimResponse, JimContactList, JimAddContact, JimDelContact
from Tschat_jim.exceptions import WrongInputError

import Tschat_log.server_log_config
from Tschat_log.decorators import Log

# Получаем серверный логгер по имени, он уже объявлен в log_config и настроен
logger = logging.getLogger('server')
log = Log(logger)


class Handler():
    """Обработчик сообщений, тут будет основная логика сервера"""

    def __init__(self):
        # сохраняем репозиторий
        self.repo = Repo(session)

    def read_requests(self, r_clients, all_clients):
        """
        Чтение сообщений, которые будут посылать клиенты
        :param r_clients: клиенты которые могут отправлять сообщения
        :param all_clients: все клиенты
        :return:
        """
        # Список входящих сообщений
        messages = []

        for sock in r_clients:
            try:
                # Получаем входящие сообщения
                message = get_message(sock)
                # Добавляем их в список
                # В идеале нам нужно сделать еще проверку, что сообщение нужного формата прежде чем его пересылать!
                # Пока оставим как есть, этим займемся позже
                messages.append((message, sock))
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)

        # Возвращаем словарь сообщений
        return messages

    @log
    def write_responses(self, messages, names, all_clients):
        """
        Отправка сообщений тем клиентам, которые их ждут
        :param messages: список сообщений
        :param w_clients: клиенты которые читают
        :param all_clients: все клиенты
        :return:
        """

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
                    # в цикле по контактам шлем сообщения
                    # for contact in contacts:
                    #     message = JimContactList(contact.Name)
                    #     print(message.to_dict())
                    #     send_message(sock, message.to_dict())
                    contact_names = [contact.Name for contact in contacts]
                    message = JimContactList(contact_names)
                    send_message(sock, message.to_dict())
                elif action.action == ADD_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.repo.add_contact(username, user_id)
                        # формируем удачный ответ
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
                        # формируем удачный ответ
                        response = JimResponse(ACCEPTED)
                        # Отправляем
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        # формируем ошибку, такого контакта нет
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        # Отправляем
                        send_message(sock, response.to_dict())
                elif action.action == MSG:
                    to = action.to
                    client_sock = names[to]
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
        # Делаем проверки
        try:
            presence = Jim.from_dict(presence_message)
            username = presence.account_name
            if not self.repo.client_exists(username):
                self.repo.add_client(username)
        except Exception as e:
            response = JimResponse(WRONG_REQUEST, error=str(e))
            return response.to_dict(), None
        else:
            response = JimResponse(OK)
            return response.to_dict(), username


class Server:
    """Класс сервера"""

    def __init__(self, handler):
        """
        :param handler: обработчик событий
        """
        self.handler = handler
        self.clients = []
        self.names = {}
        self.sock = socket(AF_INET, SOCK_STREAM)

    def bind(self, addr, port):
        self.sock.bind((addr, port))

    def listen_forever(self):
        self.sock.listen(15)
        self.sock.settimeout(0.2)
        print('Сервер запущен')

        while True:
            try:
                conn, addr = self.sock.accept()
                presence = get_message(conn)
                response, client_name = self.handler.presence_response(presence)
                send_message(conn, response)
            except OSError as e:
                pass
            else:
                print('Получен запрос на соединение от {}'.format(addr))
                self.clients.append(conn)
                self.names[client_name] = conn
                print('К нам подключился {}'.format(client_name))
            finally:
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass

                requests = self.handler.read_requests(r, self.clients)
                self.handler.write_responses(requests, self.names, self.clients)


def main():
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = ''
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)

    handler = Handler()
    server = Server(handler)
    server.bind(addr, port)
    server.listen_forever()

if __name__ == '__main__':
    main()
