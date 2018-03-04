from __future__ import division

from typing import List, Union


def convert_string_to_int_or_none(s):
    # type: (str) -> Union[int, None]
    if s == "None":
        return None
    else:
        return int(s)


def convert_int_or_none_to_string(v):
    if v is None:
        return "None"
    else:
        return str(v)


def convert_string_to_int(s):
    # type: (str) -> int
    return int(s)


def convert_string_to_int_default(i, s):
    # type: (int, str) -> int
    if s.startswith("+"):
        return i+int(s[1:])
    if s.startswith("-"):
        return i-int(s[1:])
    if s.startswith("*"):
        return i*int(s[1:])
    if s.startswith("/"):
        return i//int(s[1:])


def convert_int_to_string(i):
    # type: (int) -> str
    return str(i)


def convert_string_to_bool(s):
    # type: (str) -> bool
    if s in {"true", "True", "yes", "Yes", "1", "y", "Y", "t", "T"}:
        return True
    return False


def convert_bool_to_string(b):
    # type: (bool) -> str
    return str(b)


def convert_string_to_list_int(s):
    # type: (str) -> List[int]
    return [int(x) for x in s.split(",")]


def convert_list_int_to_string(li):
    # type: (List[int]) -> str
    return str(li)


def convert_string_to_list_str(s):
    # type: (str) -> List[str]
    return [x for x in s.split(",")]


def convert_list_str_to_string(li):
    # type: (List[str]) -> str
    return str(li)


def convert_string_to_string(e):
    # type: (str) -> str
    return e
