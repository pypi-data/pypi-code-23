import inspect
import threading
from collections import namedtuple
try:
    import cffi
    global_ffi = cffi.FFI()
except ImportError:
    cffi = global_ffi = None


class FFI(object):
    _tracking = {}
    _track_item = namedtuple("track_item", ('ffi', 'depth'))

    def __init__(self, ffi=None):
        """
        Can be used to start a closure from an existing compiled module or ffi instance
        :param ffi or module ffi: ffi instance to encapsulate
        """
        if ffi is not None:
            closure = self._tracking.get(self._track_id)
            if closure and closure.ffi is not ffi:
                raise ValueError("Can't start a new ffi context while already within one")
            else:
                self.ffi = ffi.ffi if hasattr(ffi, 'ffi') else ffi
        else:
            closure = self._tracking.get(self._track_id)
            self.ffi = closure.ffi if closure else global_ffi

    def __repr__(self):
        return repr(self.ffi)

    @property
    def _track_id(self):
        return threading.get_ident()

    def __enter__(self):
        """
        Once a context manager has been started, any subsequent calls to FFI() during that
        call stack will return the ffi instance the context manager was started with
        :return: ffi instance
        """
        closure = self._tracking.get(self._track_id)
        if not closure:
            # Start a new closure
            self._tracking[self._track_id] = self._track_item(self.ffi, 1)
        else:
            self._tracking[self._track_id] = self._track_item(self.ffi, closure.depth + 1)
        return self.ffi

    def __exit__(self, exc_type, exc_val, exc_tb):
        closure = self._tracking.get(self._track_id)
        depth = closure.depth - 1
        if depth:
            self._tracking[self._track_id] = self._track_item(self.ffi, depth)
        else:
            # closure finished
            del self._tracking[self._track_id]

    def __getattr__(self, item):
        return getattr(self.ffi, item)
