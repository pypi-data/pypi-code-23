from typing import List

from .media_type import MediaType
from .rel import RelValue
from ..renderer import SirenBase


class Link(SirenBase):
    def __init__(self, rel: List[RelValue], href: str, title: str=None, type: MediaType=None, classes: List[str]=None):
        self._rel = rel
        self._href = href
        self._title = title
        self._type = type
        self._class = classes
