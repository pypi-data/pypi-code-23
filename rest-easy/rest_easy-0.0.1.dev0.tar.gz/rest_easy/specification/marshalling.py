"""Marshal resources for various HTTP methods."""


from typing import Callable, Union

from rest_easy.specification import Specification


def marshall_with(func: Union[Callable, object], spec: Specification):
    pass
