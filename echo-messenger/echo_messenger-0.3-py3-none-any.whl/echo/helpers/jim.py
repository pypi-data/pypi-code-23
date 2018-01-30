import json
import time

MESSAGE_SIZE = 1024
DELIMITER = '\n\r'
DATE_FORMAT = ' %I:%M%p'


class Message:
    def __init__(self, **kwargs):
        self.__raw = kwargs
        self.__raw['time'] = time.strftime(DATE_FORMAT)

    def __bytes__(self):
        return '{}{}'.format(json.dumps(self.__raw), DELIMITER).encode()

    def __str__(self):
        return str(self.__raw)

    @property
    def action(self):
        return self.__raw['action'] if 'action' in self.__raw else None

    @property
    def response(self):
        return self.__raw['response'] if 'response' in self.__raw else None

    @property
    def quantity(self):
        return self.__raw['quantity'] if 'quantity' in self.__raw else None

    @property
    def user_account_name(self):
        try:
            name = self.__raw['user']['account_name']
        except ValueError:
            return None
        return name

    @property
    def account_name(self):
        try:
            name = self.__raw['account_name']
        except ValueError:
            return None
        return name

    @property
    def user_name(self):
        try:
            name = self.__raw['user_name']
        except ValueError:
            return None
        return name

    @property
    def destination(self):
        return self.__raw['to'] if 'to' in self.__raw else None

    @property
    def sender(self):
        return self.__raw['_from'] if '_from' in self.__raw else None

    @property
    def error(self):
        return self.__raw['error'] if 'error' in self.__raw else None

    @property
    def text(self):
        return self.__raw['text'] if 'text' in self.__raw else None


def success(response=200, **kwargs):
    return Message(response=response, **kwargs)


def error(text, **kwargs):
    return Message(response=400, error=text, **kwargs)


def error_request(text, **kwargs):
    return Message(action='error', msg=text, **kwargs)


def receive(sock, logger):
    requests = []
    try:
        raw_bytes = sock.recv(MESSAGE_SIZE)
    except UnicodeDecodeError as e:
        msg = 'Connection reset'
        logger.info(msg)
        requests.append(error_request(msg))
        return []

    try:
        raw_string = raw_bytes.decode()
    except UnicodeDecodeError as e:
        msg = 'Got not unicode message {}'.format(e)
        logger.info(msg)
        requests.append(error_request(msg))
    else:
        try:
            raw_strings = list(filter(None, raw_string.split(DELIMITER)))
            messages = list(map(json.loads, raw_strings))
        except ValueError as e:
            msg = 'Got not valid json "{}"'.format(raw_string)
            logger.info(msg)
            requests.append(error_request(msg))
        else:
            logger.info('Received {}'.format(list(messages)))
            requests.extend(list(Message(**msg) for msg in messages))
    return requests
