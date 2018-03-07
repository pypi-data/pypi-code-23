# encoding: utf-8

import logging_helper
from pprint import pformat
from future.builtins import str as text

logging = logging_helper.setup_logging()


class LogLines(object):

    _JOINER = u'\n' + 87 * u' '  # TODO: remove hardcoded 87 spaces

    def __init__(self,
                 name=None,
                 level=logging_helper.INFO,
                 log_lines=None):
        self.level = level
        self.name = name
        self._init_log_lines()
        if log_lines:
            self.append(log_lines)

    def _init_log_lines(self):
        self.log_lines = []
        if self.name:
            self.append(self.name)

    def append(self,
               line):
        # Being nice to bad users by handling lists
        # here as well as extend
        if isinstance(line, list):
            self.extend(line)
            return

        # Lets try to be nice to everything else too...
        if not isinstance(line, (str, text)):
            line = pformat(line)

        # Using extend on the split string in
        # is contains newlines.
        self.log_lines.extend(line.split(u'\n'))

    def extend(self,
               lines):
        for line in lines:
            # Not using extend in case there are
            # new lines in individual strings.
            self.append(line)

    def push(self):
        # TODO: get caller for push for the log message otherwise you get logging_helper.multi_line_logger
        if any(self.log_lines):
            logging.log(level=self.level,
                        msg=self._JOINER.join(self.log_lines))
            self._init_log_lines()

    def __del__(self):
        self.push()
