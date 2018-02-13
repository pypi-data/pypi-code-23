from typing import Union, Tuple, Type, Any, Dict, List, TypeVar

# Argument type is either:
#  - str: name
#  - tuple: (name)
#  - tuple: (name, type)
#  - tuple: (name, type, default)
# Type also might be a tuple of types
# For 'Any' type, use object or None
ArgumentType = Union[str, Tuple[str], Tuple[str, Type], Tuple[str, Tuple[Type]], Tuple[str, Type, Any], Tuple[str, Tuple[Type], Any]]
ArgumentListType = Union[List[ArgumentType], None]
CanonicalArgumentType = Tuple[str, Tuple[Type], Any, bool]
CanonicalArgumentListType = List[CanonicalArgumentType]

class ArgumentError(Exception):
    pass
class ArgumentValueError(ArgumentError, ValueError):
    pass
class ArgumentTypeError(ArgumentError, TypeError):
    pass

class MethodNotAllowedError(Exception):
    pass