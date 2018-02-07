from functools import wraps


class Log:
    """Класс-декоратор для оборачивания функций подлежащих логированию."""

    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def _create_message(result=None, *args, **kwargs):
        """
        Формирует сообщение для записи в лог
        :param result: результат работы функции
        :param args: любые параметры по порядку
        :param kwargs: любые именованные параметры
        :return:
        """
        message = ''
        if args:
            message += 'args: {} '.format(args)
        if kwargs:
            message += 'kwargs: {} '.format(kwargs)
        if result:
            message += '= {}'.format(result)

        return message

    def __call__(self, func):
        """
        Определяем __call__ для возможности вызова экземпляра как декоратора
        :param func: функция которую будем декорировать
        :return: новая функция
        """
        @wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            message = Log._create_message(result, *args, **kwargs)
            self.logger.debug('{} - {} - {}'.format(message, decorated.__name__, decorated.__module__))
            return result

        return decorated