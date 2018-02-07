import asyncio
import logging
from enum import Enum
from typing import Any, Dict, Callable, Tuple, Sequence

import rethinkdb as R
import rethinkdb.ast as ast

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'process_functions', 'prettify_value', 'NotYetImplementException',
    'ensure_element', 'ensure_sequence', 'ensure_dict', 'check_equals'
]

_log = logging.getLogger(__name__)


class NotYetImplementException(Exception):
    """
    Exception that caused when you use some function or method than not yet implemented for this part of functionallity and exists
    only to implement abstract classes
    """


def process_functions(fields_dict: Dict, init_function: Callable, configure_function: Callable, definer_ignore: bool = False) -> Tuple[Callable, Callable]:
    for key, value in sorted(fields_dict.items(), key=lambda x: x[0]):
        # Skip service values
        if value.service:
            continue
        # To keep compatibility for cases when we use fields without model
        # for example, like service configuration for cartridges
        if value.name is None:
            value.name = key
        if not (value.definer and definer_ignore):
            init_function = value.wrap_function_with_parameter(
                init_function,
                required=not value.optional,
                use_default=True
            )
        if value.reconfigurable or (value.definer and not definer_ignore):
            configure_function = value.wrap_function_with_parameter(
                configure_function,
                required=not value.reconfigurable,
                use_default=False
            )
    return init_function, configure_function


def prettify_value(value) -> Any:
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, list):
        return [prettify_value(x) for x in value]
    if isinstance(value, tuple):
        return tuple(prettify_value(x) for x in value)
    if isinstance(value, dict):
        return {prettify_value(k): prettify_value(v) for k, v in value.items()}
    return value


async def ensure_element(element):
    if isinstance(element, asyncio.Future):
        return await element
    if isinstance(element, (list, tuple)):
        return await ensure_sequence(element)
    if isinstance(element, dict):
        await ensure_dict(element)
    return element


async def ensure_sequence(sequence: Sequence) -> Sequence:
    return [await ensure_element(x) for x in sequence]


async def ensure_dict(model_dict: Dict) -> Dict:
    for key, value in model_dict.items():
        if isinstance(value, asyncio.Future):
            model_dict[key] = await value
        if isinstance(value, dict):
            await ensure_dict(value)
        if isinstance(value, (list, tuple)):
            model_dict[key] = await ensure_sequence(value)
    return model_dict


def check_equals(first_query: R.RqlQuery, second_query: R.RqlQuery) -> bool:  # pylint: disable=too-many-return-statements
    if first_query.__class__ != second_query.__class__:
        return False
    if first_query.__class__ == ast.Datum:
        return first_query.data == second_query.data
    if first_query.__class__ == ast.MakeArray:
        return len(first_query._args) == len(second_query._args)
    if first_query.__class__ == ast.Var:
        return True
    if len(first_query._args) != len(second_query._args):
        return False
    if first_query.__class__ == ast.And:
        return (
            (check_equals(first_query._args[0], second_query._args[0]) and check_equals(first_query._args[1], second_query._args[1]))
            or
            (check_equals(first_query._args[0], second_query._args[1]) and check_equals(first_query._args[1], second_query._args[0]))
        )
    for index in range(0, len(first_query._args)):
        if not check_equals(first_query._args[index], second_query._args[index]):
            return False
    return True
