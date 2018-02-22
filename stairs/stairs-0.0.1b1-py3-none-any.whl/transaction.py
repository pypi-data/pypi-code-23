import sqlalchemy as sa
from sqlalchemy.pool import NullPool

from . import errors
from . import session
from . import settings
from . import states


class Transaction(object):
    """
    An elementary step of the transaction stairs
    """

    def __init__(self):
        self._engine = None
        self._conn = None
        self._txn = None
        self._session = None

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    def __enter__(self):
        self.__verify_reentrance()
        self.__connect_and_begin()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.__commit()
            finalized = None

        elif exc_type is states.Committed:
            self.__commit()
            finalized = True

        elif exc_type is states.RolledBack:
            self.__rollback()
            finalized = True

        else:
            self.__rollback()
            finalized = False

        self.__cleanup()

        return finalized

    def __verify_reentrance(self):
        if any((
                self._engine,
                self._conn,
                self._txn,
                self._session,
        )):
            raise errors.StepAlreadyEntered()

    def __connect_and_begin(self):
        self.__init_engine()

        self._conn = self._engine.connect()
        self._txn = self._conn.begin()
        self._session = session.Session(
            bind=self._conn,
            origin=self,
        )

    def __init_engine(self):
        self.__verify_db()

        self._engine = sa.create_engine(
            settings.DATABASE_URL,
            encoding='utf-8',
            poolclass=NullPool,
        )

    def __verify_db(self):
        if not settings.DATABASE_URL:
            raise errors.InvalidDatabase()

    def __commit(self):
        self._session.flush()
        self._txn.commit()

    def __rollback(self):
        self._session.rollback(internal=True)
        self._txn.rollback()

    def __cleanup(self):
        self._conn.close()

        self._conn = None
        self._txn = None
        self._session = None
