from abc import ABCMeta, abstractmethod


class BaseTransmitter(metaclass=ABCMeta):

    def __init__(self):
        print("constructor")

    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def subscribe(self, subject, message_handler): pass

    @abstractmethod
    def unsubscribe(self, subject): pass

    @abstractmethod
    def publish(self, subject, message): pass

    @abstractmethod
    def close(self): pass