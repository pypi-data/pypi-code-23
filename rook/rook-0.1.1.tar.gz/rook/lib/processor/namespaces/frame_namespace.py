
import inspect
import six

from .namespace import Namespace
from .container_namespace import ContainerNamespace
from .python_object_namespace import PythonObjectNamespace


class FrameNamespace(Namespace):

    def __init__(self, frame):
        super(FrameNamespace, self).__init__(self.METHODS)

        self.frame = frame
        self.frame_info = inspect.getframeinfo(frame, 0)

    def read_attribute(self, name):
        if name in self.frame.f_locals:
            return PythonObjectNamespace(self.frame.f_locals[name])
        elif name in self.frame.f_globals:
            return PythonObjectNamespace(self.frame.f_globals[name])
        else:
            raise KeyError("Item does not exist!", name)

    def filename(self, args=None):
        return PythonObjectNamespace(self.frame_info[0])

    def line(self, args=None):
        return PythonObjectNamespace(self.frame_info[1])

    def function(self, args=None):
        return PythonObjectNamespace(self.frame_info[2])

    def module(self, args=None):
        module = inspect.getmodule(self.frame)
        if module:
            return PythonObjectNamespace(module.__name__)
        else:
            return PythonObjectNamespace(None)

    def locals(self, args=None):
        result = {}
        for name, value in six.iteritems(self.frame.f_locals):
            ns = PythonObjectNamespace(value)
            if name == 'self':
                ns.dump_config = PythonObjectNamespace.ObjectDumpConfig.conservative_limits(value)
            result[name] = ns

        return ContainerNamespace(result)

    def globals(self, args):
        return PythonObjectNamespace(self.frame.f_globals)

    def dump(self, args):
        return ContainerNamespace({
            'locals': self.locals(),
            'module': self.module(),
            'filename': self.filename(),
            'line': self.line(),
            'function': self.function(),
        })

    METHODS = (filename, line, function, module, locals, globals, dump)
