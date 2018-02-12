from typing import List

from .media_type import MediaType
from .method import Method
from ..renderer import SirenBase
from .field import Field


class Action(SirenBase):
    def __init__(self, name: str, href: str,
                 title: str=None, method: Method=Method.GET,
                 classes: List[str]=None,
                 type: MediaType=MediaType('application/x-www-form-urlencoded'),
                 fields: List[Field]=None):
        self._name = name
        self._href = href
        self._title = title
        self._method = method
        self._class = classes
        self._type = type
        self._fields = fields
