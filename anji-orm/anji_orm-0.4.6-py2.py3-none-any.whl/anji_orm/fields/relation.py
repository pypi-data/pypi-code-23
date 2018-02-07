import asyncio
import functools
from typing import List

import rethinkdb as R

from .base import AbstractField
from ..core import register
from ..utils import ensure_element

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['LinkField', 'LinkListField']


def set_to_cache(model_class, parent_model_record, model_id, result):
    if isinstance(result, asyncio.Future):
        result = result.result()
    parent_model_record.shared.relation_cache[model_class._table][model_id] = result


def get_model_and_load_to_cache(model_class, parent_model_record, model_id):
    if register.async_mode:
        result: asyncio.Task = asyncio.ensure_future(model_class.async_get(model_id))
        result.add_done_callback(functools.partial(set_to_cache, model_class, parent_model_record, model_id))
    else:
        result = model_class.get(model_id)
        set_to_cache(model_class, parent_model_record, model_id, result)
    return result


class LinkField(AbstractField):

    def __init__(self, model_class, **kwargs) -> None:
        super().__init__(
            str,
            description=model_class.__doc__,
            default=None,
            **kwargs
        )
        self._model_class = model_class
        self._table_name = model_class._table
        self._table = R.table(self._table_name)

    def real_value(self, model_record):
        return model_record._values.get(self.name)

    async def async_format(self, value) -> str:  # pylint: disable=no-self-use
        return self.format(await ensure_element(value))

    def __get__(self, instance, instance_type):
        if instance is None:
            # when name not None
            # that mean that field for already processed
            # and will be used only in comparation
            if self.name is not None:
                return self._query_row
            return self
        model_id = instance._values.get(self.name)
        result = instance.shared.relation_cache[self._table_name].get(model_id)
        if result is None:
            if model_id is not None:
                result = get_model_and_load_to_cache(self._model_class, instance, model_id)
        return result


class LinkListField(AbstractField):

    def __init__(self, model_class, **kwargs) -> None:
        super().__init__(
            list,
            description=model_class.__doc__,
            default=None,
            **kwargs
        )
        self._model_class = model_class
        self._table_name = model_class._table
        self._table = R.table(model_class._table)
        self._created_list: List = []

    def _fetch_from_model_list(self, instance) -> List[str]:
        value_ids = [x.id for x in self._created_list]
        instance._values[self.name] = value_ids
        return value_ids

    def real_value(self, model_record):
        if self._created_list is not None:
            return self._fetch_from_model_list(model_record)
        return model_record._values[self.name]

    async def async_format(self, value) -> str:  # pylint: disable=no-self-use
        return self.format(await ensure_element(value))

    def __get__(self, instance, instance_type):
        if instance is None:
            # when name not None
            # that mean that field for already processed
            # and will be used only in comparation
            if self.name is not None:
                return self._query_row
            return self
        if self._created_list is None:
            self._created_list = []
            model_ids = instance._values.get(self.name)
            if model_ids:
                for model_id in model_ids:
                    result = instance.shared.relation_cache[self._table_name].get(model_id)
                    if result is None:
                        if model_id is not None:
                            result = get_model_and_load_to_cache(self._model_class, instance, model_id)
                    self._created_list.append(result)
        return self._created_list

    def __set__(self, instance, value) -> None:
        if value is not None and not isinstance(value, self.param_type):
            raise ValueError(f'Field {self.name} value should have {str(self.param_type)} type instead of {value}')
        if value:
            for value_record in value:
                if not isinstance(value_record, (self._model_class, asyncio.Future, str)):
                    raise ValueError(f"This field only for model for {self._model_class}")
        # None value should be converted to empty list
        if self._created_list is not None:
            self._created_list.clear()
        if not value:
            self._created_list = []
            instance._values[self.name] = []
        elif isinstance(value[0], str):
            self._created_list = None
            instance._values[self.name] = value
        else:
            self._created_list = value
            self._fetch_from_model_list(instance)
