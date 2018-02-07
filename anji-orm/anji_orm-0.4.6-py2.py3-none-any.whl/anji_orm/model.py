from typing import Dict, Any, Type, List, overload, Optional, AsyncIterable
from datetime import datetime
from abc import ABCMeta
import logging
from importlib import import_module
from weakref import WeakValueDictionary

import rethinkdb as R

from .core import register
from .fields import DatetimeField, AbstractField, JsonField, StringField
from .utils import ensure_dict
from .syntax import AbstractIndexPolicy, GreedyIndexPolicy, RethinkDBQueryParser, QueryAst

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['SharedEnv', 'Model', 'ModelMetaclass', 'ModifyDisallowException', 'fetch', 'fetch_cursor']

MODEL_FIELDS_CONTROL = {
    '_aggregate_dict': ['_fields', '_field_marks'],
    '_aggregate_sets': ['_primary_keys'],
    '_inherit_field': ['_table']
}

BASE_COLLECTION_TYPE = (list, tuple)

_log = logging.getLogger(__name__)


class ModifyDisallowException(Exception):
    """
    Exception that raises when you try change `Model` class field that blocked for changes
    """
    pass


@overload
def fetch(rethink_dict: Dict[str, Any]) -> Optional['Model']:  # pylint: disable=unused-argument
    pass


@overload
def fetch(rethink_dict: Dict[str, Any]) -> Dict[str, Any]:  # pylint: disable=function-redefined, unused-argument
    pass


def fetch(rethink_dict: Dict[str, Any]):  # pylint: disable=function-redefined
    if '_python_info' not in rethink_dict:
        # Return just this dict, if he cannot be recognized as orm model
        return rethink_dict
    class_module = import_module(rethink_dict['_python_info']['module_name'])
    class_object = getattr(class_module, rethink_dict['_python_info']['class_name'], None)
    if class_object is None:
        _log.warning('Model record %s cannot be parsed, because class wasnt found!', rethink_dict['id'])
        return None
    obj = class_object(id_=rethink_dict['id'])
    obj.load(rethink_dict)
    return obj


async def fetch_cursor(cursor) -> AsyncIterable[Dict[str, Any]]:
    """
    Additonal method that wraps asyncio rethinkDB cursos to AsyncIterable.
    Just util method to allow async for usage
    """
    while await cursor.fetch_next():
        yield await cursor.next()


class ModelMetaclass(ABCMeta):

    @classmethod
    def _aggregate_sets(mcs, bases, namespace, field):
        actual_field = set()
        for base_class in bases:
            if hasattr(base_class, field):
                actual_field.update(getattr(base_class, field))
        if namespace.get(field, None):
            actual_field.update(namespace.get(field))
        namespace[field] = actual_field

    @classmethod
    def _aggregate_dict(mcs, bases, namespace, field):
        actual_field = {}
        for base_class in bases:
            if hasattr(base_class, field):
                actual_field.update(getattr(base_class, field))
        if namespace.get(field, None):
            actual_field.update(namespace.get(field))
        namespace[field] = actual_field

    @classmethod
    def _inherit_field(mcs, bases, namespace: Dict, field: str):
        current_field_exists = field in namespace
        if not current_field_exists:
            for base_class in bases:
                if hasattr(base_class, field):
                    namespace[field] = getattr(base_class, field)
                    break

    @classmethod
    def _block_modify(mcs, bases, namespace, field):
        if namespace.get(field) and (len(bases) > 1 or (len(bases) == 1 and bases[0] != object)):
            raise ModifyDisallowException('Field {} cannot be modified in child classes'.format(field))

    @classmethod
    def _fetch_fields(mcs, namespace):
        fields = namespace.get('_fields', None) or {}
        field_marks = {}
        primary_keys = set()
        remove_list = []
        for attr_name, attr in namespace.items():
            if getattr(attr, '_anji_orm_field', None):
                remove_list.append(attr_name)
                fields[attr_name] = attr
                attr.name = attr_name
                if attr.field_marks:
                    for field_mark in attr.field_marks:
                        field_marks[field_mark] = attr_name
                if attr.definer:
                    primary_keys.add(attr_name)
        primary_keys = sorted(primary_keys)
        namespace['_fields'] = fields
        namespace['_field_marks'] = field_marks
        namespace['_primary_keys'] = primary_keys

    @classmethod
    def _check_primary_keys(mcs, namespace):
        for field_name, field_item in namespace['_fields'].items():
            if not field_item.definer and field_name in namespace['_primary_keys']:
                namespace['_primary_keys'].remove(field_name)

    def __new__(mcs, name, bases, namespace, **kwargs):

        # Process fields

        mcs._fetch_fields(namespace)

        # Execute control actions

        for key, value in MODEL_FIELDS_CONTROL.items():
            if hasattr(mcs, key):
                for field in value:
                    getattr(mcs, key)(bases, namespace, field)

        mcs._check_primary_keys(namespace)

        # Process with register
        result = super().__new__(mcs, name, bases, namespace, **kwargs)

        if namespace.get('_table'):
            register.add_table(namespace.get('_table'), result)

        return result


class RelactionCache:  # pylint: disable=too-few-public-methods

    def __init__(self):
        self._models_cache = {}

    def __getitem__(self, key: str) -> WeakValueDictionary:
        return self._models_cache.setdefault(key, WeakValueDictionary())


class SharedEnv:

    def __init__(self):
        self._env = {}
        self.share('relation_cache', RelactionCache())

    def share(self, key: str, value: Any) -> None:
        self._env[key] = value

    def __getattr__(self, key: str) -> Any:
        if key in self._env:
            return self._env[key]
        raise AttributeError


class Model(object, metaclass=ModelMetaclass):  # pylint: disable=too-many-public-methods
    """
    Base class with core logic for rethinkdb usage.
    For usage you must define _table and _fields section.
    All object fields, that defined in _fields will be processed in send() and load() methods
    """

    _table = ''
    _fields: Dict[str, AbstractField] = {}
    _field_marks: Dict[str, AbstractField] = {}
    _primary_keys: List[str] = []
    _index_policy: Type[AbstractIndexPolicy] = GreedyIndexPolicy

    shared: SharedEnv = SharedEnv()

    orm_last_write_timestamp = DatetimeField(service=True, displayed=False)
    _python_info = JsonField(service=True, displayed=False, compute_function='_build_python_info', stored=True)
    _schema_version = StringField(service=True, displayed=False, default='v0.4', secondary_index=True)

    def _process_fields(self, fields_dict, init_kwargs) -> None:
        for key, value in fields_dict.items():
            if value.compute_function is None:
                default_value = init_kwargs.get(key, value.default)
                if callable(default_value):
                    default_value = default_value()
                setattr(self, key, default_value)

    def __init__(self, id_: str = None, **kwargs) -> None:
        """
        Complex init method for rethinkdb method.
        Next tasks will be executed:
        1. Create all fields, that defined in _fields, for object
        3. Set base fields, like connection link.
            Additionally can set id field in some cases (for example in fetch method)
        4. Create table field, to be used in queries
        """
        self._values: Dict[str, Any] = dict()
        self.id: str = id_  # pylint: disable=invalid-name
        self.table: R.RqlQuery = R.table(self._table)
        self._process_fields(self._fields, kwargs)

    def _build_python_info(self) -> Dict[str, str]:
        return {
            'module_name': self.__class__.__module__,
            'class_name': self.__class__.__name__
        }

    @classmethod
    def get_index_policy(cls) -> Type[AbstractIndexPolicy]:
        """
        Return index policy, that will be used to interact with indexes.
        See :py:mod:`~anji_orm.syntax.indexes` for mode detailes
        """
        return cls._index_policy

    def to_dict(self, full_dict: bool = False) -> Dict[str, Any]:
        """
        Utility method to generate dict from object.
        Used to send information to rethinkdb.

        :param full_dict: Build full data dict with non-stored fields
        """
        base_dict = {}
        for field_name, field_item in self._fields.items():
            if not full_dict and field_item.compute_function is not None and not field_item.stored:
                _log.debug('Skip field %s as not stored field', field_name)
                continue
            base_dict[field_name] = field_item.real_value(self)
        return base_dict

    def _apply_update_dict(self, update_dict: Dict[str, Any]) -> None:
        for _, field in self._fields.items():
            required_keys = field.update_keys()
            for key in required_keys:
                value = update_dict.get(key, None)
                if value is not None:
                    field.update_value(self, key, value)

    def update(self, update_dict: Dict[str, Any]) -> None:
        register.check_mode_consistency()
        self._apply_update_dict(update_dict)
        self.send()

    async def async_update(self, update_dict: Dict[str, Any]) -> None:
        register.check_mode_consistency(required_async=True)
        self._apply_update_dict(update_dict)
        await self.async_send()

    def send(self) -> Dict:
        """
        Method, that send information to rethinkdb.
        """
        register.check_mode_consistency()
        result = None
        self.orm_last_write_timestamp = datetime.now(R.make_timezone("00:00"))
        with register.pool.connect() as conn:
            model_dict = self.to_dict()
            if self.id is None:
                result = self.table.insert(model_dict).run(conn)
                self.id = result['generated_keys'][0]
            else:
                result = self.table.get(self.id).update(model_dict).run(conn)
                if result['skipped'] > 0:
                    model_dict['id'] = self.id
                    result = self.table.insert(model_dict).run(conn)
        return result

    async def async_send(self) -> Dict:
        register.check_mode_consistency(required_async=True)
        result = None
        self.orm_last_write_timestamp = datetime.now(R.make_timezone("00:00"))
        async with register.pool.connect() as conn:  # pylint: disable=not-async-context-manager
            model_dict = self.to_dict()
            await ensure_dict(model_dict)
            if self.id is None:
                result = await self.table.insert(model_dict).run(conn)
                self.id = result['generated_keys'][0]
            else:
                result = await self.table.get(self.id).update(model_dict).run(conn)
                if result['skipped'] > 0:
                    model_dict['id'] = self.id
                    result = await self.table.insert(model_dict).run(conn)
        return result

    def from_dict(self, rethink_dict: Dict[str, Any]) -> None:
        """
        Load model record from dict

        :param rethink_dict: dict with data from RethinkDB
        """
        for field_name, field_item in self._fields.items():
            if field_name in rethink_dict and (field_item.compute_function is None or field_item.cacheable):
                setattr(self, field_name, rethink_dict[field_name])

    def load(self, rethink_dict=None) -> None:
        """
        Method, that load information to rethinkdb.
        :param rethink_dict: rethinkdb data for this object. Useful in case, when you get this data from rethinkdb previously, for example, in fetch method.
        """
        if not rethink_dict:
            register.check_mode_consistency()
            with register.pool.connect() as conn:
                rethink_dict = self.table.get(self.id).run(conn)
        self.from_dict(rethink_dict)

    async def async_load(self, rethink_dict=None) -> None:
        if not rethink_dict:
            register.check_mode_consistency(required_async=True)
            async with register.pool.connect() as conn:  # pylint: disable=not-async-context-manager
                rethink_dict = await self.table.get(self.id).run(conn)
        self.from_dict(rethink_dict)

    def delete(self) -> None:
        """
        Method, that delete record from base table.
        Warning: you must be very patient and don't use this method with wrong connection.
        Every rethinkdb must be used only in one thread
        """
        register.check_mode_consistency()
        with register.pool.connect() as conn:
            self.table.get(self.id).delete().run(conn)

    async def async_delete(self) -> None:
        register.check_mode_consistency(required_async=True)
        async with register.pool.connect() as conn:  # pylint: disable=not-async-context-manager
            await self.table.get(self.id).delete().run(conn)

    @classmethod
    def get(cls, id_) -> R.RqlQuery:
        return cls.execute(R.table(cls._table).get(id_))

    @classmethod
    async def async_get(cls, id_) -> R.RqlQuery:
        return await cls.async_execute(R.table(cls._table).get(id_))

    @classmethod
    def count(cls, query: QueryAst = None) -> R.RqlQuery:
        if query is None:
            return cls.all().count()
        return cls.db_query(query).count()

    @classmethod
    def sample(cls, count: int, query: QueryAst = None) -> R.RqlQuery:
        if query is None:
            return cls.all().sample(count)
        return cls.db_query(query).sample(count)

    @classmethod
    def all(cls, limit: int = None, skip: int = None) -> R.RqlQuery:
        base_query = R.table(cls._table)
        if skip is not None:
            base_query = base_query.skip(skip)
        if limit is not None:
            base_query = base_query.limit(limit)
        return base_query

    def build_similarity_query(self) -> QueryAst:
        base_query: QueryAst = self.__class__._python_info == self._build_python_info()  # type: ignore
        for primary_key_part in self._primary_keys:
            base_query &= getattr(self.__class__, primary_key_part) == getattr(self, primary_key_part)
        return base_query

    def find_similar(self) -> List['Model']:
        return self.execute(self.build_similarity_query())

    async def async_find_similary(self) -> List['Model']:
        return await self.async_execute(self.build_similarity_query())

    @classmethod
    def _process_driver_response(cls, result):
        if isinstance(result, dict):
            return fetch(result)
        elif isinstance(result, list):
            return list(filter(lambda x: x is not None, (fetch(obj_data) for obj_data in result)))
        elif not result:
            return result
        return result

    @classmethod
    def execute(cls, db_query: R.RqlQuery, without_fetch: bool = False):
        register.check_mode_consistency()
        with register.pool.connect() as conn:
            result = db_query.run(conn)
        if isinstance(result, R.net.DefaultCursor):
            if without_fetch:
                return list(result)
            return list(filter(lambda x: x is not None, (fetch(obj_data) for obj_data in result)))
        if without_fetch:
            return result
        return cls._process_driver_response(result)

    @classmethod
    async def async_execute(cls, db_query: R.RqlQuery, without_fetch: bool = False):
        register.check_mode_consistency(required_async=True)
        async with register.pool.connect() as conn:  # pylint: disable=not-async-context-manager
            result = await db_query.run(conn)
        if result.__class__.__name__ == 'AsyncioCursor':
            if without_fetch:
                synced_list = [obj_data async for obj_data in fetch_cursor(result)]
                return synced_list
            synced_list = [fetch(obj_data) async for obj_data in fetch_cursor(result)]
            return list(filter(lambda x: x is not None, synced_list))
        if without_fetch:
            return result
        return cls._process_driver_response(result)

    @classmethod
    def db_query(cls, query: QueryAst) -> R.RqlQuery:
        return RethinkDBQueryParser.build_query(cls, query)

    @classmethod
    def query(cls, query: QueryAst, without_fetch: bool = False):
        builded_query = RethinkDBQueryParser.build_query(cls, query)
        return cls.execute(builded_query, without_fetch=without_fetch)

    @classmethod
    async def async_query(cls, query: QueryAst, without_fetch: bool = False):
        builded_query = RethinkDBQueryParser.build_query(cls, query)
        return await cls.async_execute(builded_query, without_fetch=without_fetch)

    @classmethod
    def unique_groups_query(cls) -> R.RqlQuery:
        return R.table(cls._table).pluck('_python_info', *cls._primary_keys).distinct()

    def to_describe_dict(self, definer_skip: bool = False) -> Dict[str, str]:
        """
        Convert record to dict with pair "Pretty field name" "Pretty field value".
        By default only field with `displayed` option will be in dict.

        :param definer_skip: Additional to not displayed skip definer fields
        """
        fields = {}
        for field_name, field_item in self._fields.items():
            if field_item.displayed and not (definer_skip and field_item.definer) and getattr(self, field_name) is not None:
                fields[field_item.description] = field_item.format(getattr(self, field_name))
        return fields

    async def async_to_describe_dict(self, definer_skip: bool = False) -> Dict[str, str]:
        fields = {}
        for field_name, field_item in self._fields.items():
            if field_item.displayed and not (definer_skip and field_item.definer) and getattr(self, field_name) is not None:
                fields[field_item.description] = await field_item.async_format(getattr(self, field_name))
        return fields
