import os
import logging
import traceback

import sys
from backend.management.remote_logging import sender


class RemoteHandler(logging.Handler):

    TAGS = "backend"

    def __init__(self):
        super(RemoteHandler, self).__init__()

    def close(self):
        pass

    def emit(self, record):
        sender.send(self._build_log(record), self.TAGS)

    def _build_log(self, record):
        return {
            'name': self.get_name(),
            'msg': record.msg,
            'formatted_message': record.getMessage(),
            'args': record.args,
            'level_name': record.levelname,
            'level_no': record.levelno,
            'path_name': record.pathname,
            'filename': record.filename,
            'module': record.module,
            'lineno': record.lineno,
            'function': record.funcName,
            'time': record.created,
            'thread_id': record.thread,
            'thread_name': record.threadName,
            'process_name': record.processName,
            'process_id': record.process,
            'traceback': traceback.format_exc(),
        }
