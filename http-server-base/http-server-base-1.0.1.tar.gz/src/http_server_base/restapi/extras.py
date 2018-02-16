from typing import Union, Tuple, Type, Any, Dict, List, TypeVar, Set

# Argument type is either:
#  - str: name
#  - tuple: (name)
#  - tuple: (name, type)
#  - tuple: (name, type, default)
# Type also might be a tuple of types
# For 'Any' type, use object or None
ArgumentType = Union \
[
    str, Tuple[str],
    Tuple[str, Union[Type, Tuple[Type], Set[Any]]],
    Tuple[str, Union[Type, Tuple[Type], Set[Any]], Any],
]
ArgumentListType = Union[List[ArgumentType], None]
CanonicalArgumentType = Tuple[str, Union[Tuple[Type], Set[Any]], Any, bool]
CanonicalArgumentListType = List[CanonicalArgumentType]

class ArgumentError(Exception):
    pass
class ArgumentValueError(ArgumentError, ValueError):
    pass
class ArgumentTypeError(ArgumentError, TypeError):
    pass

class MethodNotAllowedError(Exception):
    pass