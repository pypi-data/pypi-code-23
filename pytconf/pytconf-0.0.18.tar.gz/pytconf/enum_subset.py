from collections import OrderedDict
from enum import Enum

from typing import Type, List

from pytconf.extended_enum import str_to_enum_value, ExtendedEnum


class EnumSubset(object):
    @classmethod
    def from_enum_all(cls, e):
        # type: (Type[ExtendedEnum]) -> EnumSubset
        return EnumSubset(
            enum_type=e,
            list_of_values=e.get_list_of_all_values(),
        )

    def __init__(self, enum_type, list_of_values):
        # type: (Type[Enum], List[Type[Enum]]) -> None
        self.enum_type = enum_type
        # TODO: this should actually be an ordered set
        self.selected = OrderedDict()
        for value in list_of_values:
            self.add(value)

    def add(self, enum_value):
        assert enum_value in enum_value.__class__.__members__.values(), "bad value {}".format(enum_value)
        self.selected[enum_value] = None

    def delete(self, enum_value):
        del self.selected[enum_value]

    def yield_values(self):
        for value in self.selected.keys():
            yield value

    def values(self):
        return self.selected.keys()

    def __contains__(self, item):
        return item in self.selected

    def has_value(self, item):
        return item in {x.value for x in self.selected}

    @classmethod
    def from_string(cls, e, s):
        # type: (Type[Enum], str) -> EnumSubset
        r = EnumSubset(enum_type=e, list_of_values=[])
        for name in s.split(','):
            v = str_to_enum_value(s=name, e=e)
            r.add(v)
        return r

    def list_of_strings(self):
        my_list = []
        for x in self.selected:
            my_list.append(x.name)
        return my_list

    def to_string(self):
        return ",".join(self.list_of_strings())


def enum_subset_to_str(e):
    # type: (EnumSubset) -> str
    return e.to_string()
