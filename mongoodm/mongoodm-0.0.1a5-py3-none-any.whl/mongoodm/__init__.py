from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from pymongo.collection import Collection
from functools import partial
from flask import (
    current_app,
    _app_ctx_stack as stack
)

def convert(name):
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class DocumentCursor(object):
    """ This document cursor simply abstracts the pymongo.cursor 
    and ensures that results returned from it are of a cls type of class """
    def __init__(self, cls, cursor):
        """ Accepts the class type and pymongo cufrsor as arguments """
        self.cursor = cursor
        self.cls = cls

    # The following are special attributes used in python to tell
    # the python world this class is an iterator
    def __iter__(self):
        return self

    def __next__(self):
        value = self.cursor.next()
        if not value:
            return value

        cls = self.cls

        return cls(**value)

    # A passthrough is setup to make sure that any list like requests
    # are passed on to the pymongo cursor
    def __getitem__(self, index):
        cls = self.cls
        return cls(self.cursor.__getitem__(index))

    # Calls to any methods or properties the DocumentCursor
    # doesn't specifically have is also passed to the pymongo Cursor
    def __getattr__(self, name):
        return self.cursor.__getattribute__(name)

class DocumentMeta(type):
    _db = {}

    def __new__(cls, name, bases, clsdct):
        if '_collection' not in clsdct:
            clsdct['_collection'] = convert(name)
        return super().__new__(cls, name, bases, clsdct)

    def __init__(cls, name, bases, clsdct):
        super().__init__(name, bases, clsdct)
        if hasattr(cls, '_db') and hasattr(cls._db, 'register_class'):
            cls._db.register_class(name, cls)

    @property
    def collection(self):
        if not self._db:
            raise Exception("Database hasn't been initialised yet")
        
        return self._db.connection[self._collection]

class Document(metaclass=DocumentMeta):
    """
    The Document class is the base class for all other document types
    and defines a common subset of functionality needed for all document
    actions
    """    

    def __init__(self, *args, **kwargs):
        super().__init__()
        if '_id' in kwargs:
            kwargs['id'] = kwargs['_id']
            del kwargs['_id']
        self.__dict__.update(kwargs)

    def save(self, create_new: bool = True) -> bool:
        """ Saves the relevant document in the correct collection """
        attributes = self._filtered_attributes()
        # If there's no _id or the id is None
        if ("id" not in attributes or not attributes['id']) and create_new:
            del attributes['id']
            result = self.collection.insert_one(attributes)
            self.id = ObjectId(result.inserted_id)
            return True

        result = self.collection.update_one({"_id": self.id}, {"$set":self._filtered_attributes()}, upsert=create_new)
        if result.matched_count > 0:
            return True

        return False

    def get(self, key, value=None):
        if key in self.__dict__:
            return self[key]

        return value

    def delete(self):
        result = self.collection.delete_one({"_id": self.id})
        if result.deleted_count > 0:
            return False

        return True

    def __iter__(self):
        return iter(self._filtered_attributes().items())

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def _filtered_attributes(self) -> dict:
        """ Filters all the instance attributes if they start with two underscores """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __json__(self):
        return self._filtered_attributes()

    def to_dict(self):
        return self._filtered_attributes()

    def __str__(self):
        return "<{}.{} {}>".format(type(self).__module__, type(self).__qualname__, self._filtered_attributes())

    @classmethod
    def set_db(cls, db):
        cls._db = db

    @classmethod
    def find(cls, *args, **kwargs):
        """ Helper function to more easily run finds """
        result = cls.collection.find(*args, **kwargs)
        if not result:
            return result

        return cls._make_iterator(result)

    @classmethod
    def find_one(cls, *args, **kwargs):
        """ Helper function to more easily run finds """
        result = cls.collection.find_one(*args, **kwargs)
        if not result:
            return result

        return cls(**result)
    
    @classmethod
    def all(cls):
        return cls.find({})

    @classmethod
    def get_by_id(cls, Id):
        """ Using a string or ObjectId, grabs a relevant document """
        if isinstance(Id, str) and ObjectId.is_valid(Id):
            Id = ObjectId(Id)
        elif not isinstance(Id, ObjectId):
            raise Exception('Id was not a valid objectid')

        record = cls.collection.find_one({'_id': Id})

        if not record:
            return None

        return cls(**record)

    @classmethod
    def _make_iterator(cls, iterator):
        return DocumentCursor(cls, iterator)

class MongoODM(object):
    _supported_providers = ['mongomock', 'pymongo']
    _db = None
    

    def __init__(self, app=None, **config):
        # Save the application config
        self._registry = {}
        self.config = config

        # For working as a flask extension
        self.app = app
        if app is not None:
            self.init_app(app)

        self.Document = type(
            'Document',
            Document.__mro__,
            dict(Document.__dict__, _db=self)
        )

        

    def __enter__(self):
        return self.connection

    def __exit__(self, *args):
        pass

    def __getattr__(self, name):
        if name not in self.__dict__:
            return self._registry[name]

        return self.__getattribute__(name)

    def register_class(self, name, cls):
        self._registry[name] = cls

    def init_app(self, app):
        uri = app.config.get(
            'MONGOODM_URI',
            self.config.get('uri', 'mongodb://localhost:27017')
        )
        provider = app.config.get(
            'MONGOODM_PROVIDER',
            self.config.get('provider', 'pymongo')
        )

        self.config.update({'uri': uri, 'provider': provider})
        app.teardown_appcontext(self.teardown)

    def setup_connection(self):
        provider = self.config.get('provider', 'pymongo')
        if provider not in self._supported_providers:
            raise Exception('Specified provider is not supported')

        uri = self.config.get('uri')
        if provider == 'mongomock':
            import mongomock
            self._db = mongomock.MongoClient(self.config.get('uri'))
        elif provider == 'pymongo':
            import pymongo
            self._db = pymongo.MongoClient(self.config.get('uri'))

        return self._db


    def teardown(self, exc):
        ctx = stack.top
        if hasattr(ctx, 'mongoodm_connection'):
            ctx.mongoodm_connection.close()

    @property
    def connection(self):
        if self.app:
            ctx = stack.top
            if ctx is not None:
                if not hasattr(ctx, 'mongoodm_connection'):
                    ctx.mongoodm_connection = self.setup_connection()
                return ctx.mongoodm_connection
        else:
            if not self._db:
                self.setup_connection()
            return self._db

        return None