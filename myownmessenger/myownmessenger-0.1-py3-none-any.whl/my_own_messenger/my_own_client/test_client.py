import time
from socket import socket, AF_INET, SOCK_STREAM
from pytest import raises
from client import User
from my_own_jim.exceptions import ToLongError, ResponseCodeError, WrongDictError



class TestUser:

    def setup(self):
        self.user = User('Leo')

    # МОДУЛЬНЫЕ ТЕСТЫ
    def test_create_presence(self):
        # без параметров
        message = self.user.create_presence()
        assert message['action'] == "presence"
        # берем разницу во времени
        assert abs(message['time'] - time.time()) < 0.1
        assert message["account_name"] == 'Leo'
        # с параметром имя
        message = self.user.create_presence()
        assert message["account_name"] == 'Leo'
        # неверный тип
        with raises(TypeError):
            self.user.create_presence(200)
        with raises(TypeError):
            self.user.create_presence(None)
        # Имя пользователя слишком длинное
        with raises(ToLongError):
            u = User('11111111111111111111111111')
            u.create_presence()


    def test_translate_response(self):
        # неправильный тип
        with raises(TypeError):
            self.user.translate_response(100)
        # неверная длина кода ответа
        with raises(ResponseCodeError):
            self.user.translate_response({'response': '5'})
        # нету ключа response
        with raises(WrongDictError):
            self.user.translate_response({'one': 'two'})
        # неверный код ответа
        with raises(ResponseCodeError):
            self.user.translate_response({'response': 700})
        # все правильно
        assert self.user.translate_response({'response': 200}) == {'response': 200}


    def test_create_message(self):
        msg = self.user.create_message('to', 'hello')
        assert msg['action'] == 'msg'
        # берем разницу во времени
        assert abs(msg['time'] - time.time()) < 0.1
        assert msg['to'] == 'to'
        assert msg['from'] == 'Leo'
        assert msg['message'] == 'hello'








