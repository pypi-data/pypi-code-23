import abc
import asyncio
from itertools import combinations
import logging
from typing import Dict, Union, List, Callable, Any, Awaitable

import rethinkdb as R

from repool_forked import ConnectionPool
from async_repool import AsyncConnectionPool

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['register']

_log = logging.getLogger(__name__)

SYNC_ASYNC_TIMEOUT = 300

suitable_orm_pool = Union[ConnectionPool, AsyncConnectionPool]


class AnjoORMModeMissMatch(Exception):
    """
    Base exception, that caused when you try to use sync commands in async mode
    and async commands in sync mode
    """


class AbstractRethinkDBRegisterStrategy(abc.ABC):

    def __init__(
            self, rethinkdb_connection_kwargs: Dict[str, Union[str, int]],
            pool_size: int = 3, connection_ttl: int = 3600) -> None:
        self.rethinkdb_connection_kwargs: Dict[str, Union[str, int]] = rethinkdb_connection_kwargs
        self.pool: suitable_orm_pool = self.create_pool(pool_size, connection_ttl)

    @abc.abstractmethod
    def create_pool(self, pool_size: int, connection_ttl: int) -> suitable_orm_pool:
        pass

    @abc.abstractmethod
    def load(self) -> Union[None, Awaitable]:
        pass

    @abc.abstractmethod
    def drop_database(self) -> Union[None, Awaitable]:
        pass

    @abc.abstractmethod
    def create_secondary_index(self, table_name: str, secondary_index: str) -> Union[None, Awaitable]:
        pass

    @abc.abstractmethod
    def check_tables(self, table_list: List[str]) -> Union[None, Awaitable]:
        pass

    @abc.abstractmethod
    def check_indexes(self, table_name: str, table_models) -> Union[None, Awaitable]:
        pass

    @abc.abstractmethod
    def apply_migrations(self, table_name: str) -> Union[None, Awaitable]:
        pass

    @abc.abstractmethod
    def close(self) -> Union[None, Awaitable]:
        pass

    def build_secondary_indexes_by_fields(self, secondary_indexes_fields: List[str]) -> List[str]:  # pylint: disable=invalid-name,no-self-use
        secondary_indexes = []
        secondary_indexes.extend(secondary_indexes_fields)
        secondary_indexes_fields = sorted(secondary_indexes_fields)
        for combination_size in range(2, len(secondary_indexes_fields)):
            secondary_indexes.extend(
                (':'.join(x) for x in combinations(secondary_indexes_fields, combination_size))
            )
        secondary_indexes.append(":".join(secondary_indexes_fields))
        return secondary_indexes

    def migration_queries(self, table_name: str) -> List[R.RqlQuery]:  # pylint: disable=no-self-use
        return [
            # Migration to v0.4
            R.table(table_name).filter(lambda doc: doc.has_fields('_schema_version').not_()).replace(
                lambda record: record.without('__python_info').merge({
                    '_python_info': record['__python_info'],
                    '_schema_version': 'v0.4'
                })
            )
        ]


class SyncRethinkDBRegisterStrategy(AbstractRethinkDBRegisterStrategy):

    def create_pool(self, pool_size: int, connection_ttl: int) -> suitable_orm_pool:
        return ConnectionPool(
            pool_size=pool_size,
            conn_ttl=connection_ttl,
            **self.rethinkdb_connection_kwargs
        )

    def load(self) -> None:
        pass

    def drop_database(self) -> None:
        database_name = self.rethinkdb_connection_kwargs.get('db', None)
        with self.pool.connect() as conn:
            R.db_drop(database_name).run(conn)

    def create_secondary_index(self, table_name: str, secondary_index: str) -> None:
        _log.info("Create secondary index %s on table %s", secondary_index, table_name)
        if ':' not in secondary_index:
            with self.pool.connect() as conn:
                R.table(table_name).index_create(secondary_index).run(conn)
                R.table(table_name).index_wait(secondary_index).run(conn)
        else:
            with self.pool.connect() as conn:
                R.table(table_name).index_create(secondary_index, [R.row[x] for x in secondary_index.split(':')]).run(conn)
                R.table(table_name).index_wait(secondary_index).run(conn)

    def check_tables(self, table_list: List[str]) -> None:
        with self.pool.connect() as conn:
            exists_tables = R.table_list().run(conn)
            for table in table_list:
                if table not in exists_tables:
                    R.table_create(table).run(conn)

    def check_indexes(self, table_name: str, table_models) -> None:
        with self.pool.connect() as conn:
            full_secondary_index_list = R.table(table_name).index_list().run(conn)
            orm_required_secondary_indexes = []
            for table_model in table_models:
                secondary_indexes_fields = [field_name for field_name, field in table_model._fields.items() if field.secondary_index]
                if secondary_indexes_fields:
                    orm_required_secondary_indexes.extend(self.build_secondary_indexes_by_fields(secondary_indexes_fields))
            for secondary_index in orm_required_secondary_indexes:
                if secondary_index not in full_secondary_index_list:
                    self.create_secondary_index(table_name, secondary_index)
                    full_secondary_index_list.append(secondary_index)
            for secondary_index in full_secondary_index_list:
                if secondary_index not in orm_required_secondary_indexes:
                    _log.info('Drop secondary index %s on table %s, not required by ORM', secondary_index, table_name)
                    R.table(table_name).index_drop(secondary_index).run(conn)

    def apply_migrations(self, table_name: str) -> None:
        with self.pool.connect() as conn:
            for query in self.migration_queries(table_name):
                query.run(conn)

    def close(self) -> None:
        self.pool.release_pool()


class AsyncRethinkDBRegisterStrategy(AbstractRethinkDBRegisterStrategy):

    def create_pool(self, pool_size: int, connection_ttl: int) -> suitable_orm_pool:
        return AsyncConnectionPool(
            self.rethinkdb_connection_kwargs,
            pool_size=pool_size,
            connection_ttl=connection_ttl,
        )

    async def load(self) -> None:
        await self.pool.init_pool()

    async def drop_database(self) -> None:
        database_name = self.rethinkdb_connection_kwargs.get('db', None)
        async with self.pool.connect() as conn:
            await R.db_drop(database_name).run(conn)

    async def create_secondary_index(self, table_name: str, secondary_index: str) -> None:
        _log.info("Create secondary index %s on table %s", secondary_index, table_name)
        async with self.pool.connect() as conn:
            if ':' not in secondary_index:
                await R.table(table_name).index_create(secondary_index).run(conn)
            else:
                await R.table(table_name).index_create(secondary_index, [R.row[x] for x in secondary_index.split(':')]).run(conn)
            await R.table(table_name).index_wait(secondary_index).run(conn)

    async def check_tables(self, table_list: List[str]) -> None:
        async with self.pool.connect() as conn:
            exists_tables = await R.table_list().run(conn)
            for table in table_list:
                if table not in exists_tables:
                    await R.table_create(table).run(conn)

    async def apply_migrations(self, table_name: str) -> None:
        async with self.pool.connect() as conn:
            for query in self.migration_queries(table_name):
                await query.run(conn)

    async def check_indexes(self, table_name: str, table_models) -> None:
        async with self.pool.connect() as conn:
            full_secondary_index_list = await R.table(table_name).index_list().run(conn)
            orm_required_secondary_indexes = []
            for table_model in table_models:
                secondary_indexes_fields = [field_name for field_name, field in table_model._fields.items() if field.secondary_index]
                if secondary_indexes_fields:
                    orm_required_secondary_indexes.extend(self.build_secondary_indexes_by_fields(secondary_indexes_fields))
            for secondary_index in orm_required_secondary_indexes:
                if secondary_index not in full_secondary_index_list:
                    await self.create_secondary_index(table_name, secondary_index)
                    full_secondary_index_list.append(secondary_index)
            for secondary_index in full_secondary_index_list:
                if secondary_index not in orm_required_secondary_indexes:
                    _log.info('Drop secondary index %s on table %s, not required by ORM', secondary_index, table_name)
                    await R.table(table_name).index_drop(secondary_index).run(conn)

    async def close(self) -> None:
        await self.pool.release_pool()


class RethinkDBRegister(object):

    """
    Register object that store any information about models, tables.
    Store and control pool and wrap logic.
    """

    def __init__(self, ) -> None:
        super().__init__()
        self.tables: List[str] = []
        self.tables_model_link: Dict[str, List[Any]] = {}
        self.pool: suitable_orm_pool = None
        self.strategy: AbstractRethinkDBRegisterStrategy = None
        self.wrap_decorator: Callable = None
        self.async_mode: bool = False
        self.async_loop: asyncio.AbstractEventLoop = None

    def init(
            self, rethinkdb_connection_kwargs: Dict[str, Union[str, int]],
            pool_size: int = 3, connection_ttl: int = 3600, async_mode: bool = False) -> None:
        self.async_mode = async_mode
        if async_mode:
            R.set_loop_type('asyncio')
            self.strategy = AsyncRethinkDBRegisterStrategy(
                rethinkdb_connection_kwargs,
                pool_size=pool_size,
                connection_ttl=connection_ttl)
        else:
            self.strategy = SyncRethinkDBRegisterStrategy(
                rethinkdb_connection_kwargs,
                pool_size=pool_size,
                connection_ttl=connection_ttl
            )
        self.pool = self.strategy.pool

    def check_mode_consistency(self, required_async: bool = False) -> None:
        if self.async_mode != required_async:
            required_mode = 'async' if required_async else 'sync'
            register_mode = 'async' if self.async_mode else 'sync'
            raise AnjoORMModeMissMatch(
                f"You try to use {required_mode} mode but register loaded {register_mode} mode"
            )

    def set_wrap_decorator(self, wrap_decorator: Callable) -> None:
        """
        Just set wrapper for wrapping logic. Wrapper should be argparse-compatable.

        :param wrap_decorator: argparse-compatable function wrapper
        """
        self.wrap_decorator = wrap_decorator

    def wrap(self, function: Callable, parameter_name: str, **kwargs: Any) -> Callable:
        """
        Control point to wrap function with argparse-compatable dict.
        Before usage :any:`set_wrap_decorator` should be called.

        See also :any:`wrap_function_with_parameter`.

        :param function: Function to wrap
        :param paramater_name: argparse parameter name
        :param kwargs: argpase function keyword args
        :return: wrapped function
        """
        if self.wrap_decorator is None:
            raise Exception("Wrap decorator not configurated")
        return self.wrap_decorator(parameter_name, **kwargs)(function)

    def add_table(self, table, model_cls):
        if table and (table not in self.tables):
            self.tables.append(table)
        self.tables_model_link.setdefault(table, []).append(model_cls)

    async def async_load(self, database_setup=True) -> None:
        await self.strategy.load()
        self.async_loop = asyncio.get_event_loop()
        if database_setup:
            await self.strategy.check_tables(self.tables)
            for table_name, table_models in self.tables_model_link.items():
                await self.strategy.check_indexes(table_name, table_models)
                await self.strategy.apply_migrations(table_name)

    def load(self, database_setup=True) -> None:
        self.strategy.load()
        if database_setup:
            self.strategy.check_tables(self.tables)
            for table_name, table_models in self.tables_model_link.items():
                self.strategy.check_indexes(table_name, table_models)
                self.strategy.apply_migrations(table_name)

    def close(self) -> None:
        self.strategy.close()

    async def async_close(self) -> None:
        await self.strategy.close()


register = RethinkDBRegister()
