import json
from typing import NamedTuple

from nots.v2 import Serializer
import typing


s = """[[1], [2], [3]]"""
r = json.loads(s)

serializer = Serializer()
result = serializer.convert_to(r, typing.List[typing.List[int]], )

print(result)
print(result is r)


class A(NamedTuple):
    a: int
    b: float

s = """{
  "a": 123,
  "b": 321
}
"""

r = json.loads(s)
a = serializer.convert_to(r, A, )
print(a)


a = A(1, 2)
print(serializer.convert_from(a,,)
