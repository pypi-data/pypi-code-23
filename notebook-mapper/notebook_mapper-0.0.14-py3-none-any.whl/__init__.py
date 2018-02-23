# Copywrite James Draper 2017.
import os

def find_path():
    """Find the location of omin package in any given file system."""
    __dir_path__ = os.path.dirname(os.path.realpath(__file__))
    return __dir_path__

with open(os.path.join(find_path(), '__version__')) as f:
    __version__ = f.read().strip()

from .utils import native_cmd
from .utils import net_use
from .utils import find_mapped_drive_letter
from .utils import append_mapped
from .utils import AutoMapper
