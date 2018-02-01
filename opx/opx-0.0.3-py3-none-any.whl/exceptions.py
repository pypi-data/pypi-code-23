"""Custom exceptions"""

import logging
import sys

L = logging.getLogger('opx')


class CommandException(Exception):
    """Passes nested return value to user."""
    def __init__(self, cmd: str, code: int) -> None:
        self.msg = '[command] {cmd}'.format(cmd=cmd)
        self.msg += '\nfailed with return code {code}'.format(code=code)
        super(CommandException, self).__init__(self.msg)
        L.error(self.msg)
        sys.exit(code)


class CliException(Exception):
    """For CLI usage error."""
    def __init__(self, msg: str) -> None:
        super(CliException, self).__init__(msg)
        L.error(msg)
        sys.exit(1)
