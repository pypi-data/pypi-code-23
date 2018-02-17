# -*- coding: utf-8 -*-
"""Signal module.

contains PSSignal
"""


class PSSignal:

    """Basic signal class.

    This class is necessary because QGraphicsItems cannot have Qt signals.
    Any method can be connected to and disconnected from this signal.
    """

    def __init__(self):
        self.__methods = []

    def connect(self, method):
        """Connect method `method` to signal.

        Args:
            method (func): Method that will be run when signal is emitted.
        """
        self.__methods.append(method)

    def disconnect(self, method):
        """Disconnect method `method` from signal.

        Args:
            method (func): Method to be disconnected from the signal.
        """
        i = self.__methods.index(method)
        del self.__methods[i]

    def emit(self, *args):
        """Emit signal and run all connected methods.

        Args:
            *args: Any arguments are passed to the connected functions.
        """
        for m in self.__methods:
            m(*args)
