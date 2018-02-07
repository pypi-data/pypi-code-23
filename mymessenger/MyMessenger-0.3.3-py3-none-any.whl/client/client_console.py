import sys
import logging

from ..jim.core import *
from ..utils import start_thread
from ..logger.config import logger_config
from ..logger.decorators import Log
from .core import MyMessengerClient
from .handlers import ConsoleReceiver


logger_config('client', logging.DEBUG)
logger = logging.getLogger('client')
log = Log(logger)


class MyMessengerClientConsole:
    """Клиент my_messenger."""
    def __init__(self, account_name, password):
        self.client = MyMessengerClient(account_name, password)
        self.client_thread = None
        self.listener = None
        self.listener_thread = None

    def stop(self):
        self.listener.stop()

    def run(self, host, port):
        self.client_thread = start_thread(self.client.run, 'Client', host, port)
        while not self.client.is_alive:
            pass
        self.listener = ConsoleReceiver(self.client.socket, self.client.request_queue)
        self.listener_thread = start_thread(self.listener.poll, 'Listener')
        self.sender()
        self.client_thread.join()
        self.listener_thread.join()

    def sender_parser(self, command):
        """Обработка команд пользователя."""
        if command == '<quit>':
            self.client.stop()
        elif command == '<leave>':
            self.client.leave_room()
        elif command.startswith('<list>'):
            self.client.contact_list_request()
            self.show_contacts()
        elif command.startswith('<'):
            action, param = command.split()
            if action == '<add>':
                self.client.add_contact(param)
            elif action == '<del>':
                self.client.del_contact(param)
            elif action == '<join>':
                self.client.join_room(param)
        else:
            jm = JimMessage(self.client.room, self.client.user.account_name, command)
            self.client.request(jm)

    def sender(self):
        while self.client.is_alive:
            command = input()
            self.sender_parser(command)
        self.stop()

    def show_contacts(self):
        for contact in self.client.get_contact_list():
            print(contact)


def main():
    host = None
    port = None
    name = None
    password = None
    if len(sys.argv) >= 4:
        host = sys.argv[1]
        port = 7777

        for option in sys.argv[2:]:
            key, val = option.split('=')
            if key == '-port':
                port = val
            elif key == '-user':
                name = val
            elif key == '-pass':
                password = val

    if host and port and name and password:
        client = MyMessengerClientConsole(name, password)
        client.run(host, port)
    else:
        print('Usage: client.py <addr> [-port=<port>] -user=<user> -pass=<password>')


if __name__ == '__main__':
    main()
