import io
import os

BASE_DIR = os.path.dirname(__file__)


def data(fname):
    """Return the content of a file in the tests/data dir as a unicode string."""
    path = os.path.join(BASE_DIR, 'data', fname)
    with io.open(path, encoding='utf-8') as f:
        return f.read()
