from ..renderer import SirenBase


class FieldValueObject(SirenBase):
    def __init__(self, value: str, title: str=None, selected: bool=False):
        self._title = title
        self._value = value
        self._selected = selected
