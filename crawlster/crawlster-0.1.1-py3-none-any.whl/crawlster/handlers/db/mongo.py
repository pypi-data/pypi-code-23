try:
    import pymongo
except ImportError:
    msg = """MongoDB item handler requires PyMongo. Run

    pip install pymongo

    and then try again.
    """
    raise ImportError(msg)

from crawlster.handlers.base import BaseItemHandler
from crawlster.config import UrlOption, StringOption


class MongodbItemHandler(BaseItemHandler):
    """Mongodb item handler

    Writes the submitted items directly to a MongoDB database.

    Configuration options:

    - ``mongodb.url`` - required, mongodb connection url.
    - ``mongodb.database`` - the database to write to. Defaults to crawlster
    - ``mongodb.collection`` - the collection to write to. Defaults to
      ``crawlster_items``
    """
    config_options = {
        'mongodb.url': UrlOption(required=True),
        'mongodb.database': StringOption(default='crawlster'),
        'mongodb.collection': StringOption(default='crawlster_items')
    }

    def __init__(self):
        super(MongodbItemHandler, self).__init__()
        self._conn = None
        self._coll = None

    def initialize(self):
        """Initializes the MongoDB connection"""
        self._conn = pymongo.MongoClient(self.config.get('mongodb.url'))
        db = self._conn[self.config.get('mongodb.database')]
        self._coll = db[self.config.get('mongodb.collection')]

    def handle(self, item):
        """Persists one entry to database"""
        self._coll.insert_one(item)

    def finalize(self):
        """Closes the connection"""
        self._conn.close()
