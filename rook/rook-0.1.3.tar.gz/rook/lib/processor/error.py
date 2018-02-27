import sys

from ..lib_interfaces import rook_pb2, ToolException, ErrorConfiguration
from .namespace_serializer import NamespaceSerializer
from .namespaces.python_object_namespace import PythonObjectNamespace
from .namespaces.stack_namespace import StackNamespace


class Error(object):

    def __init__(self, exc=None, type=None, message=None, parameters=None, traceback=None):
        self.exc = exc

        if isinstance(exc, ToolException):
            self.type = exc.get_type()
            self.message = exc.get_message()
            self.parameters = exc.get_parameters()
        else:
            self.type = type or "Unknown"
            self.message = message
            self.parameters = parameters

        # Extract traceback if was not supplied
        self.traceback = traceback
        if self.traceback is None and sys.exc_info()[2]:
            self.traceback = sys.exc_info()[2].tb_frame

    def dump(self, error):
        try:
            if self.message:
                error.message = NamespaceSerializer.normalize_string(self.message)
            else:
                error.message = ''
        except Exception:
            pass

        try:
            error.type = NamespaceSerializer.normalize_string(self.type)
        except Exception:
            pass

        try:
            serializer = NamespaceSerializer()
            serializer.dump(PythonObjectNamespace(self.parameters), error.parameters, False)
        except Exception:
            pass

        try:
            serializer = NamespaceSerializer()
            serializer.dump(PythonObjectNamespace(self.exc), error.exc, False)
        except Exception:
            pass

        try:
            if self.traceback:
                serializer = NamespaceSerializer()
                serializer.dump(StackNamespace(self.traceback).traceback(ErrorConfiguration.STACK_DEPTH), error.traceback, False)
        except Exception:
            pass

    def dumps(self):
        error = rook_pb2.Error()
        self.dump(error)
        return error
