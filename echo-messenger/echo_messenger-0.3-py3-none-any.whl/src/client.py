import socket
from threading import Thread

import jim
from client import client_logger


def receiver(sock, logger, callback):
    while True:
        parcels = jim.receive(sock, logger)
        while len(parcels):
            msg = parcels.pop()
            callback(msg)


class Client:
    def __init__(self, host, name, callback):
        self.name = name
        self.__host = host
        self.__sock = socket.socket()
        self.__logger = client_logger

        self.__listen_thread = Thread(target=receiver, args=(self.__sock, self.__logger, callback))
        self.__listen_thread.daemon = True

    def connect(self):
        self.__sock.connect(self.__host)
        if not self.__send_presence():
            return False
        self.__listen_thread.start()
        return True

    def send(self, request):
        self.__logger.info('Send {}.'.format(str(request)))
        return self.__sock.send(bytes(request))

    def close(self):
        self.__listen_thread.is_alive = False
        self.__sock.close()

    def __send_presence(self, status='Yep, I am here!'):
        request = jim.Message(action='presence', user={'account_name': self.name, 'status': status})
        self.send(request)
        parcels = jim.receive(self.__sock, self.__logger)
        return parcels[0].response == 200
