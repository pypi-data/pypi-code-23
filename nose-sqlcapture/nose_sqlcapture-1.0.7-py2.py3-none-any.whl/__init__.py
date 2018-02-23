import sys
try:
    sys.modules['unicode'] = unicode
except NameError as e:
    from future.types.newstr import unicode
    sys.modules['unicode'] = unicode

from .plugin import SQLCapture  # noqa
