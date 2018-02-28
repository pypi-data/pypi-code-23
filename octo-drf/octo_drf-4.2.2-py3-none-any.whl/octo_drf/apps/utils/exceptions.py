class RootException(Exception):
    """
    Базовое исключение проекта
    """


class ModelException(RootException):
    """"
    Базовое исключение для моделей
    """


class ViewException(RootException):
    """"
    Базовое исключение для вью
    """

class UniqueConfigError(ModelException):
    """
    Исключение при дублировании уникального конфига
    """