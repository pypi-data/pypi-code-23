import select
import sys
from .server import *
from .handler import *
from my_own_jim import *
from my_own_logs import *
from socket import socket, AF_INET, SOCK_STREAM
from my_own_jim.utils import send_message, get_message
from my_own_jim.config import *
from my_own_jim.core import Jim, JimMessage, JimResponse, JimContactList, JimAddContact, JimDelContact


class Server:
    """Класс сервер"""

    def __init__(self, handler):
        """обработчик событий"""
        self.handler = handler
        # список клиентов
        self.clients = []
        # тут будут имена клиентов и их сокеты
        self.names = {}
        # сокет
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP

    def bind(self, addr, port):
        # запоминаем адрес и порт
        self.sock.bind((addr, port))
        print('Server started on {}'.format(port))

    def listen_forever(self):
        # запускаем цикл обработки событиц много клиентов
        self.sock.listen(15)
        self.sock.settimeout(0.2)

        while True:
            try:
                conn, addr = self.sock.accept()  # Проверка подключений
                # получаем сообщение от клиента
                presence = get_message(conn)
                # формируем ответ
                response, client_name = self.handler.presence_response(presence)
                # отправляем ответ клиенту
                send_message(conn, response)
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение от %s" % str(addr))
                # Добавляем клиента в список
                self.clients.append(conn)
                # нам надо связать имя клиента и его сокет
                self.names[client_name] = conn
                # проверим кто к нам подключился
                print('К нам подключился {}'.format(client_name))
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился

                requests = self.handler.read_requests(r, self.clients)  # Получаем входные сообщения
                self.handler.write_responses(requests, self.names, self.clients)  # Выполним отправку входящих сообщений



###############################################################################
def main():
    #loop
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



###############################################################################
#
###############################################################################
if __name__ == "__main__":
    main()
