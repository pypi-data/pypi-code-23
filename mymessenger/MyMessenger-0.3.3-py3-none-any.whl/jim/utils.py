import json
import time

from .config import DEBUG_MODE

# Кодировка
ENCODING = 'utf-8'


def dict_to_bytes(message_dict):
    """
    Преобразование словаря в байты
    :param message_dict: словарь
    :return: bytes
    """
    # Проверям, что пришел словарь
    if isinstance(message_dict, dict):
        # Преобразуем словарь в json
        jmessage = json.dumps(message_dict)
        # Переводим json в байты
        bmessage = jmessage.encode(ENCODING)
        # Возвращаем байты
        return bmessage
    else:
        raise TypeError


def bytes_to_dict(message_bytes):
    """
    Получение словаря из байтов
    :param message_bytes: сообщение в виде байтов
    :return: словарь сообщения
    """
    # Если переданы байты
    if isinstance(message_bytes, bytes):
        # Декодируем
        jmessage = message_bytes.decode(ENCODING)
        # Из json делаем словарь
        try:
            message = json.loads(jmessage)
            # Если там был словарь
            if isinstance(message, dict):
                # Возвращаем сообщение
                return message
            else:
                # Нам прислали неверный тип
                raise TypeError
        except json.decoder.JSONDecodeError:
            print('JSONDecodeError')
    else:
        # Передан неверный тип
        raise TypeError


def send_message(sock, message):
    """
    Отправка сообщения
    :param sock: сокет
    :param message: словарь сообщения
    :return: None
    """
    if DEBUG_MODE > 0:
        ftime = time.time()
        print('[{}] SEND: {}'.format(ftime, message))
    # Словарь переводим в байты
    bmessage = dict_to_bytes(message)
    # Отправляем
    sock.send(bmessage)


def get_message(sock):
    """
    Получение сообщения
    :param sock:
    :return: словарь ответа
    """
    # Получаем байты
    if DEBUG_MODE > 1:
        ftime = time.time()
        print('[{}] GET'.format(ftime))
    bresponse = sock.recv(1024)
    # переводим байты в словарь
    response = bytes_to_dict(bresponse)
    if DEBUG_MODE > 0:
        ftime = time.time()
        print('[{}] GET: {} '.format(ftime, response))
    # возвращаем словарь
    return response
