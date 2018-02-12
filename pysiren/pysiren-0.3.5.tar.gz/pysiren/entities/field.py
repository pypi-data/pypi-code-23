from .field_type import FieldType
from ..renderer import SirenBase


class Field(SirenBase):
    def __init__(self, name: str, title: str=None, value=None, type: FieldType=FieldType.TEXT):
        self._name = name
        self._title = title
        self._value = value
        self._type = type
