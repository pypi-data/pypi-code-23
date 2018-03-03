from typing import Callable  # NOQA
from typing import List  # NOQA
from typing import Optional  # NOQA


class OpenAPIMetadata:

    def __init__(self):
        self.tags = []  # type: List[str]
        self.operation_id = None  # type: Optional[str]
        self.summary = None  # type: Optional[str]


class OpenAPI:

    @staticmethod
    def tags(tags):
        # type: (List[str])->Callable[[type], type]
        def applicator(meta):
            # type: (OpenAPIMetadata)->None
            meta.tags = tags

        return OpenAPI._wrapper(applicator)

    @staticmethod
    def operation_id(operation_id):
        # type: (str)->Callable[[type], type]
        def applicator(meta):
            # type: (OpenAPIMetadata)->None
            meta.operation_id = operation_id

        return OpenAPI._wrapper(applicator)

    @staticmethod
    def summary(summary):
        # type: (str)->Callable[[type], type]
        def applicator(meta):
            # type: (OpenAPIMetadata)->None
            meta.summary = summary

        return OpenAPI._wrapper(applicator)

    @staticmethod
    def _wrapper(metadata_applicator):
        # type: (Callable[[OpenAPIMetadata], None])->Callable[[type], type]
        def wrapper(cls):
            # type: (type) -> type
            meta = get_metadata(cls)
            metadata_applicator(meta)
            return cls

        return wrapper


def get_metadata(cls):
    # type: (type)->OpenAPIMetadata
    if not hasattr(cls, '__open_api__'):
        cls.__open_api__ = OpenAPIMetadata()
    return cls.__open_api__
