
from clitellum.core import serialization

__author__ = 'Sergio'


class HandlerManager:

    def __init__(self):
        self.__handlers = dict()

    def handler(self, key, **options):
        def decorator(f):
            self.add_handler(key, f, options)
            return f
        return decorator

    def add_handler(self, key, class_type, options):
        self.__handlers[key] = class_type

    def get_handler(self, key):
        return self.__handlers[key]()


class HandlerBase:

    def __init__(self):
        self.__bus = None
        self.__header = None
        self.__context = None

    def initialize(self, bus, header):
        self.__bus = bus
        self.__header = header
        self.__context = header['CallContext']

    @property
    def bus(self):
        """
        :rtype: SenderGateway
        :return:
        """
        return self.__bus

    @property
    def context(self):
        return self.__context

    def handle_message(self, message):
        pass

    def _send(self, message, key):
        self.bus.send(message, key=key, header=self.__header)

    def _reply(self, message, key):
        self.bus.reply(message, key, header=self.__header)
