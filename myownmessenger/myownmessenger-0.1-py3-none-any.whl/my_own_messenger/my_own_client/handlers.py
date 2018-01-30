from my_own_jim.config import MESSAGE
from PyQt5.QtCore import QObject, pyqtSignal
from my_own_jim.utils import get_message
from my_own_jim.core import Jim, JimResponse, JimMessage
from my_own_jim.exceptions import WrongParamsError, ToLongError, WrongActionError, WrongDictError, ResponseCodeError
from my_own_jim.config import *


class Receiver:
    """Класс-получатель информации из сокета"""

    def __init__(self, sock, request_queue):
        # запоминаем очередь ответов
        self.request_queue = request_queue
        # запоминаем сокет
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        """метод для обработки принятого сообщения, будет переопределен в наследниках"""
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            data = get_message(self.sock)
            try:
                # Преобразуем словарь в Jim, Это может быть action, а может быть response
                jm = Jim.from_dict(data)

                # Если это сообщение
                if isinstance(jm, JimMessage):
                    # мы его обрабатываем
                    self.process_message(jm)
                else:
                    # Это либо ответ от сервера либо действия с контактами
                    # мы это складываем в очередь
                    self.request_queue.put(jm)
            except Exception as e:
                print(e)


    def stop(self):
        self.is_alive = False


class GuiReciever(Receiver, QObject):
    """GUI обработчик входящих сообщений"""
    # сигнал, что пришли данные
    gotData = pyqtSignal(str)
    # сигнал, что прием окончен
    finished = pyqtSignal(int)

    def __init__(self, sock, request_queue):
        # инициализируем как Receiver
        Receiver.__init__(self, sock, request_queue)
        # инициализируем как QObject
        QObject.__init__(self)

    def process_message(self, message):
        """Обработка сообщения"""
        # Генерируем сигнал
        text = '{} >>> {}'.format(message.from_, message.message)
        self.gotData.emit(text)

    def poll(self):
        super().poll()
        # При окончании обработки генерируем сигнал finished
        self.finished.emit(0)
