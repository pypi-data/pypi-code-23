"""This module initializes the Rook using default settings when imported."""
import six

from rook.interface import Rook
from rook.exceptions import RookCommunicationException

try:
    obj = Rook()
    obj.start()
except RookCommunicationException:
    six.print_("Rook failed to connect to the agent - will continue attempting in the background.")
    import traceback
    traceback.print_exc()
except BaseException:
    six.print_("Rook failed automatic initialization")
    import traceback
    traceback.print_exc()
