import time
import json
import socket
from server import presence_response, read_requests


def test_presence_response():
    # Нету ключа action
    assert presence_response({'one': 'two', 'time': time.time()}) == {'response': 400, 'error': 'Не верный запрос'}
    # Нету ключа time
    assert presence_response({'action': 'presence'}) == {'response': 400, 'error': 'Не верный запрос'}
    # Ключ не presence
    assert presence_response({'action': 'test_action', 'time': 1000.10}) == {'response': 400,
                                                                             'error': 'Не верный запрос'}
    # Кривое время
    assert presence_response({'action': 'presence', 'time': 'test_time'}) == {'response': 400,
                                                                              'error': 'Не верный запрос'}
    # Всё ок
    assert presence_response({'action': 'presence', 'time': 1000.10}) == {'response': 200}


# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# Класс заглушка для сокета
class ClientSocket():
    """Класс-заглушка для операций с сокетом"""
    def __init__(self, sock_type=socket.AF_INET, sock_family=socket.SOCK_STREAM):
        pass

    def recv(self, n):
        message = {"test": "test_message"}
        jmessage = json.dumps(message)
        bmessage = jmessage.encode()
        return bmessage


def test_read_requests(monkeypatch):
    monkeypatch.setattr("socket.socket", ClientSocket)
    r_clients = [socket.socket(), socket.socket()]
    all_clients = [socket.socket(), socket.socket(), socket.socket()]
    result = [
       {'test': 'test_message'},
       {'test': 'test_message'}
    ]
    print(read_requests(r_clients, all_clients))
    print(result)
    assert read_requests(r_clients, all_clients) == result