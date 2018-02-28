"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
import sys

from .__version__ import __version__
from .vlab import Vlab
from .vlab_hci_device import VirtualHciDevice, BluezError
from .jemu_interrupts import Interrupts


class PythonVersionException(Exception):
    pass


if not sys.version_info[0] == 2 or not sys.version_info[1] == 7:
    raise PythonVersionException("python version should be 2.7")
