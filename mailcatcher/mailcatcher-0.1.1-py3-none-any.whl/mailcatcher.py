# std lib
import json
from threading import Thread

# community lib
import requests
from websocket import create_connection
from rx.subjects import Subject
from rx.concurrency import ThreadPoolScheduler

# package lib
from . import message

class Mailcahtcher:

    @staticmethod
    def parse_message(m):
        """Parse a message

        Returns:
            message.Message
        """
        return message.Message(
            m['id'],
            m['recipients'],
            m['sender'],
            m['size'],
            m['subject'],
            m['type'],
            m['source'],
            m['created_at'])

    def __init__(self, host: str, port: int):
        """
        Arguments:
            host {str} -- Host name
            port {int} -- Port number
        """

        # domain
        self.__domain = '{host}:{port}'.format(host = host, port = port)

        # ThreadPool
        self._pool_scheduler = ThreadPoolScheduler(1)

    def messages(self):
        """Get a list of messages.

        Returns:
            List[message.Message] -- List of messages
        """
        return map(Mail.parse_message, requests.get('http://{domain}/messages'.format(domain = self.__domain)).json())

    def get_message_by_id(self, message_id: int):
        """Retrieve message.

        Arguments:
            message_id {int} -- ID
        """
        return requests.get('http://{domain}/messages/{message_id}.plain'.format(domain = self.__domain, message_id = message_id, type = type)).text

    def observable(self):
        """Return Observable object of Message.

        Returns:
            Observable[message.Message] -- Observable of messages
        """

        stream = Subject()

        def ws(stream: Subject):
            """Thread Process
            """
            ws = create_connection('ws://{domain}/messages'.format(domain = self.__domain))
            while True:
                stream.on_next(Mail.parse_message(json.loads(ws.recv())))

        th = Thread(target=ws, name='Mailcahtcher_ws', args=(stream,))
        th.start()

        return stream.subscribe_on(self._pool_scheduler)
