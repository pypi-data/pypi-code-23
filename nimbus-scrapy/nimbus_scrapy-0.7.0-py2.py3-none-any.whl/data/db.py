# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""
Package Description
"""
import os
import sys
import logging
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import ConcreteBase, AbstractConcreteBase, DeferredReflection
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy import MetaData
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy.orm import load_only
from ..decorator import singleton, singleton_

__all__ = ["client", "ClientDB", "Base", ]

DEFAULT_NAME = "default"

Base = declarative_base()


@singleton_
class ClientDB(object):
    SESSION = "session"
    ENGINE = "engine"
    connections = {}

    def init(self, name=None, **kwargs):
        if not name:
            return None
        if name in self.connections:
            return self.get_session(name)
        _dialect = kwargs.pop("dialect", "")
        _db = kwargs.pop("db", "")
        _user = kwargs.pop("user", "")
        _password = kwargs.pop("password", "")
        _host = kwargs.pop("host", "")
        _port = kwargs.pop("port", "")
        _db_uri = kwargs.pop("db_uri", "")
        _uri = kwargs.pop("uri", "")
        _uri_format = _uri or _db_uri
        uri = _uri_format.format(dialect=_dialect, host=_host, port=_port, db=_db, user=_user, password=_password)
        _autocommit = kwargs.pop("autocommit", False)
        _autoflush = kwargs.pop("autoflush", True)
        _autocreate = kwargs.pop("autocreate", False)
        params = {k: str(v) if isinstance(v, basestring) else v for k, v in kwargs.iteritems()}
        db_engine = create_engine(uri, **params)
        db_session = scoped_session(sessionmaker(autocommit=_autocommit, autoflush=_autoflush, bind=db_engine))
        self.connections[name] = {
            self.SESSION: db_session,
            self.ENGINE: db_engine,
        }
        if _autocreate:
            self.create_db(name=name)
            self.create_table(name=name)
        return self.get_session(name)

    def get_session(self, name=DEFAULT_NAME):
        info = self.connections.get(name, {})
        return info.get(self.SESSION, None)

    def get_engine(self, name=DEFAULT_NAME):
        info = self.connections.get(name, {})
        return info.get(self.ENGINE, None)

    def create_db(self, name=DEFAULT_NAME):
        _engine = self.get_engine(name)
        if not _engine:
            raise RuntimeError("No DB Engine")
        metadata = MetaData(_engine)
        metadata.create_all()

    def create_table(self, name=DEFAULT_NAME):
        _engine = self.get_engine(name)
        if not _engine:
            raise RuntimeError("No DB Engine")
        Base.metadata.create_all(bind=_engine)


client = ClientDB()
