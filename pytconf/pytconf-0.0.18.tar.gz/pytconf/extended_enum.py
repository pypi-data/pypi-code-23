from enum import Enum
from typing import Type, List


class ExtendedEnum(Enum):

    @classmethod
    def get_list_of_all_values(cls):
        return [x for x in cls.__members__.values()]

    @classmethod
    def from_string(cls, s):
        # type: (str) -> Type[Enum]
        for x in cls:
            if s == x.name:
                return x
        raise ValueError("cannot find value [{}]".format(s))


def enum_type_to_list_str(e):
    # type: (Type[Enum]) -> List[str]
    a = [x.name for x in e]
    return a


def enum_value_to_str(ev):
    # type: (Type[Enum]) -> str
    return ev.name


def str_to_enum_value(s, e):
    # type: (str, Type[Enum]) -> Type[Enum]
    for x in e:
        if s == x.name:
            return x
    raise ValueError("cannot find value [{}]".format(s))


def str_to_enum_int(s, e):
    # type: (str, Type[Enum]) -> int
    for x in e:
        if s == x.name:
            return x.value
    raise ValueError("cannot find value [{}]".format(s))


def enum_int_to_name(i, e):
    # type: (int, Type[Enum]) -> str
    for x in e:
        if i == x.value:
            return x.name
    raise ValueError("cannot find value [{}]".format(i))
