
import inspect
import platform

from .namespace import Namespace
from .collection_namespace import ListNamespace, DictNamespace
from .container_namespace import ContainerNamespace
from .python_object_namespace import PythonObjectNamespace
from .frame_namespace import FrameNamespace

# Fixing a bug in PyPy
if 'PyPy' == platform.python_implementation():
    import sys
    FakeFrameType = type(sys._current_frames().values()[0])
    from types import TracebackType, FrameType

    def isframe(object):
        return isinstance(object, (FrameType, FakeFrameType))

    inspect.isframe = isframe


class StackNamespace(Namespace):

    DEFAULT_TRACEBACK_DEPTH = 1000
    DEFAULT_FRAMES_DEPTH = 100

    def __init__(self, frame):
        super(StackNamespace, self).__init__(self.METHODS)
        self._frame = frame

    def read_attribute(self, name):
        raise NotImplementedError("StackNamespace does not support attribute read!")

    def read_key(self, key):
        pos = int(key)

        current_frame = self._frame
        for i in range(pos):
            current_frame = current_frame.f_back

        return FrameNamespace(current_frame)

    def traceback(self, args):
        if args:
            depth = int(args)
        else:
            depth = self.DEFAULT_TRACEBACK_DEPTH

        result = []

        current_frame = self._frame
        for i in range(depth):
            frame_info = inspect.getframeinfo(current_frame, 0)

            module = inspect.getmodule(current_frame)
            if module:
                module_name = module.__name__
            else:
                module_name = None

            result.append(ContainerNamespace({
                'module': PythonObjectNamespace(module_name),
                'filename': PythonObjectNamespace(frame_info[0]),
                'line': PythonObjectNamespace(frame_info[1]),
                'function': PythonObjectNamespace(frame_info[2])
            }))

            current_frame = current_frame.f_back
            if not current_frame:
                break

        return ListNamespace(result)

    def frames(self, args):
        if args:
            depth = int(args)
        else:
            depth = self.DEFAULT_FRAMES_DEPTH

        result = []

        current_frame = self._frame
        for i in range(depth):
            result.append(FrameNamespace(current_frame).dump(None))

            current_frame = current_frame.f_back
            if not current_frame:
                break

        return ListNamespace(result)

    METHODS = (traceback, frames)
