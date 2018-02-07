import time as ctime

from .config import *
from .exceptions import WrongParamsError, TooLongError, WrongActionError, WrongDictError, ResponseCodeError, \
    IsNotJimUser


class MaxLengthField:
    """Дескриптор, ограничивающий размер поля."""
    def __init__(self, name, max_length):
        """
        :param name: имя поля
        :param max_length: максимальная длина
        """
        self.max_length = max_length
        self.name = '_' + name

    def __set__(self, instance, value):
        """Установка значения поля с проверкой его длины."""
        # если длина поля больше максимального значения
        if len(value) > self.max_length:
            # вызываем ошибку
            raise TooLongError(self.name, value, self.max_length)
        # иначе записываем данные в поле
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        # получаем данные поля
        return getattr(instance, self.name)


class Jim:
    """Реализация JIM-протокола."""

    def to_dict(self):
        """Родителький метод для потомков."""
        return {}

    @staticmethod
    def try_create(jim_class, input_dict):
        """Создание объекта JIM из словаря"""
        try:
            return jim_class(**input_dict)
        except KeyError:
            raise WrongParamsError(input_dict)

    @staticmethod
    def from_dict(input_dict):
        """Подготовка входного словаря к использованию при создании объекта JIM методом try_create()."""
        """
        :input_dict: входной словарь
        :return: объект Jim: Action или Response
        """
        # должно быть response или action
        # если action
        if ACTION in input_dict:
            # достаем действие
            action = input_dict.pop(ACTION)
            # действие должно быть в списке действий
            if action in ACTIONS:
                if action == PRESENCE:
                    user_dict = input_dict.pop(USER)
                    user = JimUser(user_dict[ACCOUNT_NAME])
                    input_dict.update({USER: user})
                    return Jim.try_create(JimPresence, input_dict)
                elif action == AUTHENTICATE:
                    user_dict = input_dict.pop(USER)
                    user = JimUser(user_dict[ACCOUNT_NAME], user_dict[PASSWORD])
                    input_dict.update({USER: user})
                    return Jim.try_create(JimAuthenticate, input_dict)
                elif action == GET_CONTACTS:
                    return Jim.try_create(JimGetContacts, input_dict)
                elif action == CONTACT_LIST:
                    return Jim.try_create(JimContactList, input_dict)
                elif action == ADD_CONTACT:
                    return Jim.try_create(JimAddContact, input_dict)
                elif action == DEL_CONTACT:
                    return Jim.try_create(JimDelContact, input_dict)
                elif action == JOIN:
                    return Jim.try_create(JimJoin, input_dict)
                elif action == LEAVE:
                    return Jim.try_create(JimLeave, input_dict)
                elif action == QUIT:
                    return Jim.try_create(JimQuit, input_dict)
                elif action == MSG:
                    try:
                        input_dict['from_'] = input_dict['from']
                    except KeyError:
                        raise WrongParamsError(input_dict)
                    del input_dict['from']
                    return Jim.try_create(JimMessage, input_dict)
            else:
                raise WrongActionError(action)
        elif RESPONSE in input_dict:
            return Jim.try_create(JimResponse, input_dict)
        else:
            raise WrongDictError(input_dict)


class JimAction(Jim):
    """Класс-родитель для классов JIM-сообщений типа action"""

    def __init__(self, action, time=None):
        self.action = action
        if time:
            self.time = time
        else:
            self.time = ctime.time()

    def to_dict(self):
        result = super().to_dict()
        result[ACTION] = self.action
        result[TIME] = self.time
        return result


class JimAddContact(JimAction):
    """Добавить контакт."""
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)
    # Имя пользователя ограничено 25 символов - используем дескриптор
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    def __init__(self, account_name, user_id, time=None):
        self.account_name = account_name
        self.user_id = user_id
        super().__init__(ADD_CONTACT, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        result[USER_ID] = self.user_id
        return result


class JimDelContact(JimAction):
    """Удалить контакт."""
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)
    # Имя пользователя ограничено 25 символов - используем дескриптор
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    def __init__(self, account_name, user_id, time=None):
        self.account_name = account_name
        self.user_id = user_id
        super().__init__(DEL_CONTACT, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        result[USER_ID] = self.user_id
        return result


class JimContactList(JimAction):
    """Сообщение типа Контакт при передаче списка контактов."""
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    def __init__(self, user_id, quantity=0, time=None):
        self.user_id = user_id
        self.quantity = quantity
        super().__init__(CONTACT_LIST, time)

    def to_dict(self):
        result = super().to_dict()
        result[USER_ID] = self.user_id
        result[QUANTITY] = self.quantity
        return result


class JimGetContacts(JimAction):
    """Запрос списка контактов"""
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)

    def __init__(self, account_name, quantity=0, time=None):
        self.account_name = account_name
        self.quantity = quantity
        super().__init__(GET_CONTACTS, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        result[QUANTITY] = self.quantity
        return result


class JimPresence(JimAction):
    """Приветствие JIM"""
    def __init__(self, user, time=None):
        if not isinstance(user, JimUser):
            raise IsNotJimUser
        self.user = user
        super().__init__(PRESENCE, time)

    def to_dict(self):
        result = super().to_dict()
        result[USER] = self.user.to_dict(PRESENCE)
        return result


class JimMessage(JimAction):
    """Сообщение от пользователя"""
    to = MaxLengthField('to', USERNAME_MAX_LENGTH)
    from_ = MaxLengthField('from_', USERNAME_MAX_LENGTH)
    message = MaxLengthField('message', MESSAGE_MAX_LENGTH)

    def __init__(self, to, from_, message, time=None):
        self.to = to
        self.from_ = from_
        self.message = message
        super().__init__(MSG, time=time)

    def to_dict(self):
        result = super().to_dict()
        result[TO] = self.to
        result[FROM] = self.from_
        result[MESSAGE] = self.message
        return result


class JimJoin(JimAction):
    """Присоединиться к чату."""
    room = MaxLengthField('room', ROOMNAME_MAX_LENGTH)

    def __init__(self, room, time=None):
        self.room = room
        super().__init__(JOIN, time=time)

    def to_dict(self):
        result = super().to_dict()
        result[ROOM] = self.room
        return result


class JimLeave(JimAction):
    """Покинуть чат."""
    room = MaxLengthField('room', ROOMNAME_MAX_LENGTH)

    def __init__(self, room, time=None):
        self.room = room
        super().__init__(LEAVE, time=time)

    def to_dict(self):
        result = super().to_dict()
        result[ROOM] = self.room
        return result


class JimQuit(JimAction):
    """Выход. Вежливое отключение клиента от сервера."""
    def __init__(self, time=None):
        super().__init__(QUIT, time=time)

    def to_dict(self):
        result = super().to_dict()
        return result


class JimAuthenticate(JimAction):
    """Аутентификация клиента."""
    def __init__(self, user, time=None):
        if not isinstance(user, JimUser):
            raise IsNotJimUser
        self.user = user
        super().__init__(AUTHENTICATE, time)

    def to_dict(self):
        result = super().to_dict()
        result[USER] = self.user.to_dict(AUTHENTICATE)
        return result


class ResponseField:
    """Класс-дескриптор для JIM-сообщений типа response."""
    def __init__(self, name):
        """
        :param name: имя поля
        """
        self.name = '_' + name

    def __set__(self, instance, value):
        # если значение кода не входит в список доступных кодов
        if value not in RESPONSE_CODES:
            # вызываем ошибку
            raise ResponseCodeError(value)
        # иначе записываем данные в поле
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        # получаем данные поля
        return getattr(instance, self.name)


class JimResponse(Jim):
    """Класс-родитель для классов JIM-сообщений типа response"""
    # Используем дескриптор для поля ответ от сервера
    response = ResponseField('response')

    def __init__(self, response, error=None, alert=None):
        self.response = response
        self.error = error
        self.alert = alert

    def to_dict(self):
        result = super().to_dict()
        result[RESPONSE] = self.response
        if self.error is not None:
            result[ERROR] = self.error
        if self.alert is not None:
            result[ALERT] = self.alert
        return result


class JimUser:
    """Класс, содержащий информацию о клиенте в формате JIM."""
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)
    password = MaxLengthField('password', PASSWORD_MAX_LENGTH)

    def __init__(self, account_name, password='', status=''):
        self.account_name = account_name
        self.password = password
        self.status = status

    def to_dict(self, action):
        result = {}
        result[ACCOUNT_NAME] = self.account_name
        if action == PRESENCE:
            result[STATUS] = self.status
        elif action == AUTHENTICATE:
            result[PASSWORD] = self.password
        return result