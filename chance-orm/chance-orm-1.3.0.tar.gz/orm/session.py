#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: orm/session.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 01.02.2018
"""Database Connection
"""
import logging

from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from orm.base import DBBase


LOGGER = logging.getLogger(__name__)


class DBSessionMaker(object):
    """An instance of sessionmaker.
    """
    __session_maker = None
    __values = {
        'user': None, 'password': None, 'host': None, 'port': None,
        'database': None,
    }
    base = declarative_base(cls=DBBase)

    @classmethod
    def connect(cls, **kwargs):
        """Initialize connection with given arguments

        User, Password, Host, Port, Database is required, and KeyError raised
        if not in given arguments.
        """
        cls.__values = {
            key: val for key, val in kwargs.items() if key in cls.__values
        }

        try:
            cls.__engine = create_engine(
                (
                    u'mysql+mysqldb://{user}:{password}@{host}:{port}/'
                    u'{database}?charset=utf8'
                ).format(**cls.__values), pool_recycle=3600, encoding="utf8",
            )
        except Exception, e:
            LOGGER.exception(e)
        else:
            LOGGER.info("Successfully Build Connection")
            cls.Session = scoped_session(sessionmaker(bind=cls.__engine))

    @classmethod
    def create_all(cls):
        """Create all tables in metadata
        """
        cls.base.metadata.create_all(cls.__engine)
        cls.Session.close()

    @classmethod
    def drop_all(cls):
        """Drop all tables in metadata
        """
        cls.Session.close()
        cls.base.metadata.drop_all(cls.__engine)

    @classmethod
    def close(cls):
        """Close connection
        """
        cls.Session.close()
        cls.__engine.dispose()

    @classmethod
    def with_session(cls, rollback=False, nested=False):
        """Decorator for creating session context around function.

        Wrap the function with a session created from scoped session. If
        subtransaction is True, a savepoint is created in this context to
        ensure that rollback only to this point.

        Example:

        .. code-block:: python

            @with_session
            def A(some_arguments, session):
                pass

        Notice that only in keywords can you pass your own session rather than
        the created session, or a TypeError will raise for multiple arguments
        of session passed into the same function. In other works, following
        code will raise a TypeError:

        .. code-block:: python

            @with_session
            def A(some_arguments, session):
                pass

            A('test', your_own_session) # Raise TypeError
            A('test', session=your_own_session) # Safe

        Args:
            rollback: a boolean controls whether rollback in the end.
            nested: a boolean controls whether the transaction is nested.

        Return:
            a wrapped func
        """
        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                session = kwargs.pop('session', cls.Session())
                kwargs['session'] = session

                exit_action = session.rollback if rollback else session.commit

                if nested:
                    session.begin_nested()
                    LOGGER.info('Sub session start')
                LOGGER.info('Session start')

                try:
                    result = func(*args, **kwargs)
                except Exception, e:
                    LOGGER.exception(e)
                    session.rollback()
                    raise e
                else:
                    exit_action()
                    LOGGER.info('Session exit in normal')
                finally:
                    session.close()

                return result

            return wrapper
        return decorator
