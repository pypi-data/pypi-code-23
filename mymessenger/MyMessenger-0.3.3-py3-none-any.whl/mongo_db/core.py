import time

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from .config import MONGO_DB_HOST


"""
[
    {'to': to,
    'from': from,
    'messages': [
            {'time': time
            'message': message},
    ]},
]
"""


class MongoRepo:
    """Хранилище на MongoDB"""

    def __init__(self):
        """
        Timeout for MongoDB connection, ms
        :param host: MongoDB host
        """
        maxSevSelDelay = 1000
        try:
            self.client = MongoClient(MONGO_DB_HOST, serverSelectionTimeoutMS=maxSevSelDelay)
            self.client.server_info()
            self.connected = True
        except ServerSelectionTimeoutError as err:
            print('MongoDB ERROR: {}', format(err))
            print('You may continue, but offline messages will be not work')
            self.connected = False
        self.db = self.client.mm_client_db

    def push(self, from_, to, message):
        """
        Add message to DB
        :param from_:
        :param to:
        :param message:
        :return: None if no connection to DB
        """
        if not self.connected:
            return
        result = self.db.messages.update_one(
            {
                'from': from_,
                'to': to,
            },
            {
                '$push': {
                    'messages': {
                        'time': time.time(),
                        'message': message
                    }
                }
            }
        )
        if result.matched_count == 0:
            self.db.messages.insert(
                {
                    'from': from_,
                    'to': to,
                    'messages': [
                        {
                            'time': time.time(),
                            'message': message
                        }
                    ]
                }
            )

    def pop(self, from_=None, to=None):
        """
        Generator. Get offline messages for client.
        :param from_:
        :param to:
        :return: None if no connection to DB
        """
        if not self.connected:
            return
        d = {}
        if from_:
            d.update({'from': from_})
        if to:
            d.update({'to': to})
        for msg in self.db.messages.find(d):
            self.db.messages.remove({'from': msg['from'], 'to': msg['to']})
            yield msg

    def get_all(self):
        """
        Generator. Show all messages in DB. Uses for dev.
        :return: None if no connection to DB
        """
        if not self.connected:
            return
        for item in self.db.messages.find():
            yield item
