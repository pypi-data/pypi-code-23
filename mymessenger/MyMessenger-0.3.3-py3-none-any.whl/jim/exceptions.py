class WrongInputError(Exception):
    """Базовый класс для потомков типа Неверные входные данные."""
    pass


class WrongParamsError(WrongInputError):
    """Неверные параметры для действия."""

    def __init__(self, params):
        self.params = params

    def __str__(self):
        return 'Wrong action params: {}'.format(self.params)


class WrongActionError(WrongInputError):
    """Когда передано неверное действие."""

    def __init__(self, action):
        self.action = action

    def __str__(self):
        return 'Wrong action: {}'.format(self.action)


class WrongDictError(WrongInputError):
    """Когда пришел неправильный словарь."""

    def __init__(self, input_dict):
        self.input_dict = input_dict

    def __str__(self):
        return 'Wrong input dict: {}'.format(self.input_dict)


class TooLongError(Exception):
    """Ошибка когда наше поле длинее чем надо."""

    def __init__(self, name, value, max_length):
        """
        :param name: имя поля
        :param value: текущее значение
        :param max_length: максимальное значение
        """
        self.name = name
        self.value = value
        self.max_length = max_length

    def __str__(self):
        return '{}: {} to long (> {} symbols)'.format(self.name, self.value, self.max_length)


class ResponseCodeError(Exception):
    """Неверный код ответа."""

    def __init__(self, code):
        self.code = code

    def __str__(self):
        return 'Wrong response code: {}'.format(self.code)


class IsNotJimUser(Exception):
    """Данные о пользователя не в формате JIM."""

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return '{} is not instance of JimUser class'.format(self.obj)