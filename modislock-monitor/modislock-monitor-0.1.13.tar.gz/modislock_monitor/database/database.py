# coding: UTF-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Configuration
from modislock_monitor.extensions import mon_config


config = mon_config
engine = create_engine(config.SQLALCHEMY_DATABASE_URI,
                       echo=config.SQLALCHEMY_ECHO,
                       pool_pre_ping=True)
                       # pool_recycle=config.SQLALCHEMY_POOL_RECYCLE,
                       # pool_size=5)
session_maker = sessionmaker(bind=engine)

Base = declarative_base()


class Database(object):
    """Database session

    Holds the common session used in all database transactions
    """
    def __init__(self):
        self._session = scoped_session(session_maker)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.remove()

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        self._session = session
