# Copyright 2018 Alexandru Catrina
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function

import timeit

class Console(object):
    """Console wrapper.

    Attributes:
        start_time (int): Start time of console logging.
        stop_time (int): Stop time of console logging.
        verbose (bool): Set verbose level on or off.
    """
    start_time, stop_time = 0, 0
    verbose = False

    @classmethod
    def log(cls, message=None):
        """Print log message.

        Args:
            message (str): Optional message to display.
        """
        print("[Log] %s" % message)

    @classmethod
    def start(cls, message=None):
        """Start console timer.

        Args:
            message (str): Optional message to display on start-up.
        """
        cls.start_time = timeit.default_timer()
        if cls.verbose and message is not None:
            print("[Build] %s" % message)

    @classmethod
    def stop(cls, message=None):
        """Stop console timer.

        Args:
            message (str): Optional message to display on end.
        """
        cls.stop_time = timeit.default_timer()
        if cls.verbose and message is not None:
            print("\033[92m[Build] %s\033[0m" % message)
        print("\033[92m\033[1m[Build] OK (runtime %ss)\033[0m" % (cls.stop_time - cls.start_time))

    @classmethod
    def warn(cls, message):
        """Console simple warn message.

        Args:
            message (str): Message to display.
        """
        if cls.verbose:
            print(u"\033[93m[Build] %s\033[0m" % message)

    @classmethod
    def info(cls, message):
        """Console simple info message.

        Args:
            message (str): Message to display.
        """
        if cls.verbose:
            print(u"\033[92m[Build] %s\033[0m" % message)

    @classmethod
    def eval(cls, message):
        """Console response message.

        Args:
            message (str): Message to display.
        """
        if cls.verbose:
            print(u"\033[93m[Yield] %s\033[0m" % message)

    class fatal(SystemExit):
        """Console fatal error message.

        Args:
            err (str): Error to display.
        """
        def __init__(self, err):
            error = u"\033[91m[Fatal] %s\033[0m" % unicode(err)
            super(self.__class__, self).__init__(error)

    class debug(Exception):
        """Console debug error message.

        Args:
            err (str): Error to display.
        """
        def __init__(self, err):
            error = u"\033[93m[Error] %s\033[0m" % unicode(err)
            super(self.__class__, self).__init__(error)


def timeit_log(func):
    def wrapper(*args, **kwargs):
        Console.start()
        retval = func(*args, **kwargs)
        Console.stop()
        return retval
    return wrapper
