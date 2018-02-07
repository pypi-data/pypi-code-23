"""Shay Palachy's personal common Python 3 utility functions and classes."""

import utilp.classes as classes  # noqa: F401
import utilp.func as func  # noqa: F401

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# cleaning the module's name space
for name in ['get_versions', '_version', 'utilp', 'name']:
    try:
        globals().pop(name)
    except KeyError:
        pass
