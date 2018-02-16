import re
from typing import Union, Tuple, Type, Any, Dict, List, TypeVar

re_type = type(re.compile(r'some_regular'))
JsonSerializable = Union[str, int, float, Dict[str, 'JsonSerializable'], List['JsonSerializable']]
