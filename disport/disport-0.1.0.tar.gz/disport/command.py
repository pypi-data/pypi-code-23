# -*- coding: utf-8 -*-

import subprocess


class Command:
    """Stores shell command as a string.

    Provides the following methods:
        1) call(feedback=False)

    Provides the following operators:
        1) str(cmd)
        2) cmd + str
        3) cmd += str
    """
    def __init__(self, cmd=""):
        """Applies initial command to private member."""
        self._cmd = cmd

    def call(self, feedback=False):
        """Calls shell command and my return shell output."""
        # Split string into an array to be process by subprocess
        cmd = self._cmd.strip().split(" ")
        if feedback:
            # Call command and convert byte array to string
            return subprocess.check_output(cmd).decode("utf-8")
        else:
            # Just call the command
            subprocess.call(cmd)
            return None

    def __str__(self):
        """Return command as a string."""
        return self._cmd

    def __radd__(self, other):
        """Append string to command and return the result."""
        try:
            return self._cmd + " " + str(other)
        except:
            return NotImplemented

    def __iadd__(self, other):
        """Append string to command, store the result and return it."""
        try:
            self._cmd += " " + str(other)
            return self
        except:
            return NotImplemented
