"""Custom exceptions"""

import logging
import sys

L = logging.getLogger('opx')


class CliException(Exception):
    """Passes nested return value to user."""
    def __init__(self, cmd: str, code: int) -> None:
        self.msg = f'[command] {cmd}'
        self.msg += f'\nfailed with return code {code}'
        super(CliException, self).__init__(self.msg)
        L.error(self.msg)
        sys.exit(code)
