import datetime
import decimal
import enum
import inspect
import numbers
import typing

import frozendict  # type: ignore
import git  # type: ignore
import jsonpath_ng  # type: ignore
import typing_inspect  # type: ignore
from pytypes import type_util  # type: ignore


# None is not allowed because we are using it to signal a removal of metadata in update.
KNOWN_IMMUTABLE_TYPES = (
    bool, numbers.Integral, numbers.Complex, decimal.Decimal, numbers.Real, str, bytes, datetime.date, datetime.time,
    datetime.datetime, datetime.timedelta, datetime.tzinfo, datetime.timezone, type(None),
    enum.Enum,
)


def current_git_commit(path: str) -> str:
    """
    Returns a git commit hash of the repo at or above ``path``.

    Parameters
    ----------
    path : str
        A path to repo or somewhere under the repo.

    Returns
    -------
    str
        A git commit hash.
    """

    repo = git.Repo(path=path, search_parent_directories=True)
    return repo.head.object.hexsha


# Using typing.TypeVar in type signature does not really work, so we are using type instead.
# See: https://github.com/python/typing/issues/520
def get_type_arguments(cls: type) -> typing.Dict[type, type]:
    """
    Returns a mapping between type arguments and their types of a given class ``cls``.

    Parameters
    ----------
    cls : type
        A class to return mapping for.

    Returns
    -------
    Dict[TypeVar, type]
        A mapping from type argument to its type.
    """

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    result: typing.Dict[type, type] = {}

    for base_class in inspect.getmro(typing_inspect.get_origin(cls)):
        if base_class == typing.Generic:
            break

        if not typing_inspect.is_generic_type(base_class):
            continue

        parameters = typing_inspect.get_parameters(base_class)

        # We are using _select_Generic_superclass_parameters and not get_Generic_parameters
        # so that we can handle the case where the result is None.
        # See: https://github.com/Stewori/pytypes/issues/20
        arguments = type_util._select_Generic_superclass_parameters(cls, base_class)

        if arguments is None:
            arguments = [typing.Any] * len(parameters)

        if len(parameters) != len(arguments):
            raise TypeError("Number of parameters does not match number of arguments.")

        for parameter, argument in zip(parameters, arguments):
            if parameter == argument:
                argument = typing.Any

            if parameter in result:
                if result[parameter] != argument:
                    raise TypeError("Different types for same parameter across class bases: {type1} vs. {type2}".format(
                        type1=result[parameter],
                        type2=argument,
                    ))
            else:
                result[parameter] = argument

    type_parameter_names = [parameter.__name__ for parameter in result.keys()]

    type_parameter_names_set = set(type_parameter_names)

    if len(type_parameter_names) != len(type_parameter_names_set):
        for name in type_parameter_names_set:
            type_parameter_names.remove(name)
        raise TypeError("Same name reused across different type parameters: {extra_names}".format(extra_names=type_parameter_names))

    return result


def is_instance(obj: typing.Any, cls: type) -> bool:
    # "bound_typevars" argument has to be passed for this function to
    # correctly work with type variables.
    # See: https://github.com/Stewori/pytypes/issues/24
    return type_util._isinstance(obj, cls, bound_typevars={})


def is_subclass(subclass: type, superclass: type) -> bool:
    # "bound_typevars" argument has to be passed for this function to
    # correctly work with type variables.
    # See: https://github.com/Stewori/pytypes/issues/24
    return type_util._issubclass(subclass, superclass, bound_typevars={})


def is_instance_method_on_class(method: typing.Any) -> bool:
    if is_class_method_on_class(method):
        return False

    if inspect.isfunction(method):
        return True

    if getattr(method, '__func__', None):
        return True

    return False


def is_class_method_on_class(method: typing.Any) -> bool:
    return inspect.ismethod(method)


def is_instance_method_on_object(method: typing.Any, object: typing.Any) -> bool:
    if not inspect.ismethod(method):
        return False

    if method.__self__ is object:
        return True

    return False


def is_class_method_on_object(method: typing.Any, object: typing.Any) -> bool:
    if not inspect.ismethod(method):
        return False

    if method.__self__ is type(object):
        return True

    return False


def is_type(obj: typing.Any) -> bool:
    return isinstance(obj, type) or typing_inspect.is_tuple_type(obj) or typing_inspect.is_union_type(obj)


def to_json_value(value: typing.Any) -> typing.Any:
    # Metadata removes None values, so we encode it into a string,
    # together with other values which are not primitive JSON values.
    if isinstance(value, (str, int, float, bool)):
        return value
    else:
        return repr(value)


class Enum(enum.Enum):
    """
    An implementation of `Enum` base class whose instances are equal to their string names, too.
    """

    def __eq__(self, other):  # type: ignore
        if isinstance(other, str):
            return self.name == other

        return super().__eq__(other)

    # It must hold a == b => hash(a) == hash(b). Because we allow enums to be equal to names,
    # the easiest way to assure the condition is to hash everything according to their names.
    def __hash__(self):  # type: ignore
        return hash(self.name)


# Return type has to be "Any" because mypy does not support enums generated dynamically
# and complains about missing attributes when trying to access them.
def create_enum_from_json_schema_enum(class_name: str, obj: typing.Dict, json_path: str) -> typing.Any:
    json_path_expression = jsonpath_ng.parse(json_path)

    names = [match.value for match in json_path_expression.find(obj)]

    # Make the list contain unique names. It works in Python 3.6+ because dicts are ordered.
    names = list(dict.fromkeys(names))

    return Enum(class_name, {name: value for value, name in enumerate(names, start=1)})  # type: ignore


def make_immutable_copy(obj: typing.Any, _path: typing.List[typing.Any] = None) -> typing.Any:
    """
    Converts a given ``obj`` into an immutable copy of it, if possible.

    Parameters
    ----------
    obj : any
        Object to convert.
    _path : list(any)
        Current path during ``obj`` traversal.

    Returns
    -------
    any
        An immutable copy of ``obj``.
    """

    # To prevent an import cycle.
    from . import metadata

    if _path is None:
        _path = [obj]

    if isinstance(obj, KNOWN_IMMUTABLE_TYPES):
        # Because str is among known immutable types, it will not be picked apart as a sequence.
        return obj
    if obj is metadata.ALL_ELEMENTS:
        return obj
    if is_type(obj):
        # Assume all types are immutable.
        return obj
    if isinstance(obj, typing.Mapping):
        # We simply always preserve order of the mapping. Because we want to make sure also mapping's
        # values are converted to immutable values, we cannot simply use MappingProxyType.
        return frozendict.FrozenOrderedDict((make_immutable_copy(k, _path + [k]), make_immutable_copy(v, _path + [k])) for k, v in obj.items())
    if isinstance(obj, typing.Set):
        return frozenset(make_immutable_copy(o, _path + [o]) for o in obj)
    if isinstance(obj, tuple):
        # To preserve named tuples.
        return type(obj)(make_immutable_copy(o, _path + [o]) for o in obj)
    if isinstance(obj, typing.Sequence):
        return tuple(make_immutable_copy(o, _path + [o]) for o in obj)

    raise TypeError("{obj} at {path} is not known to be immutable.".format(obj=obj, path=_path))
