"""Common utility functions for Python 3."""

from ._path import (  # noqa: F401
    is_pathname_valid,
    is_path_creatable,
    path_exists_or_creatable,
    is_path_sibling_creatable,
    path_exists_or_creatable_portable,
)
# cleaning the module's name space
for name in ['_path', 'name']:
    try:
        globals().pop(name)
    except KeyError:
        pass
