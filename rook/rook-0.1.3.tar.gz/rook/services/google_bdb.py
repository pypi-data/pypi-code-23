import os
import six
import inspect

from . import cdbg_native
from .module_explorer import GetCodeObjectAtLine

from rook.lib.logger import logger

from ..exceptions import RookBdbCodeNotFound, RookBdbSetBreakpointFailed

_flags = None
cdbg_native.InitializeModule(_flags)


class Bdb(object):

    def __init__(self):
        self.frame_behind = True

        self.fncache = {}

        self._cookies = {}

        self.user_line = None

    def set_trace(self):
        # Not needed
        pass

    def canonic(self, filename):
        if filename[0] == "<" and filename[-1] == ">":
            return filename
        canonic = self.fncache.get(filename)
        if not canonic:
            canonic = os.path.abspath(filename)
            canonic = os.path.normpath(canonic)
            self.fncache[filename] = canonic
        return canonic

    def ignore_current_thread(self):
        # Not needed
        pass

    def set_break(self, module, filename, lineno):
        status, code_object = GetCodeObjectAtLine(module, lineno)
        if not status:
            raise RookBdbCodeNotFound(code_object)

        # Install the breakpoint
        cookie = cdbg_native.SetConditionalBreakpoint(code_object, lineno, None, self._callback)
        if not cookie:
            raise RookBdbSetBreakpointFailed()

        self._cookies[filename, lineno] = cookie

    def clear_break(self, filename, lineno):
        pos = filename, lineno
        try:
            cookie = self._cookies[pos]
        except KeyError:
            return

        cdbg_native.ClearConditionalBreakpoint(cookie)
        del self._cookies[pos]

    def clear_all_breaks(self):
        for cookie in six.itervalues(self._cookies):
            cdbg_native.ClearConditionalBreakpoint(cookie)

        self._cookies = {}

    def close(self):
        pass

    def _callback(self, event, frame):

        if event != cdbg_native.BREAKPOINT_EVENT_HIT:
            logger.error("Unexpected event- %d", event)
            return

        if frame and self.user_line:
            self.user_line(frame)
