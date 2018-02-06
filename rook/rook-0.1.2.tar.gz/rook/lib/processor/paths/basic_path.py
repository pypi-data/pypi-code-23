
import six
import re

from ..namespaces.container_namespace import ContainerNamespace

from ...lib_interfaces import RookAttributeNotFound, RookInvalidBasicPath, RookOperationReadOnly


class BasicPath(object):

    NAME = "basic"

    def __init__(self, configuration):
        if isinstance(configuration, six.string_types):
            string = configuration
        else:
            string = configuration['path']

        self._path_operations = []
        self._last_operation = None

        self._parse_path(string, configuration)

    def read_from(self, root_namespace):
        namespace = root_namespace
        for operation in self._path_operations:
            namespace = operation.read(namespace, False)

        return self._last_operation.read(namespace, False)

    def write_to(self, root_namespace, value):
        namespace = root_namespace
        for operation in self._path_operations:
            namespace = operation.read(namespace, True)

        self._last_operation.write(namespace, value)

    def _parse_path(self, path, configuration):
        matcher = re.compile("[\w[][\w'\"()]*]?")
        raw_operations = matcher.findall(path)
        if not raw_operations:
            raise RookInvalidBasicPath(configuration)

        for operation in raw_operations[:-1]:
            self._path_operations.append(self._build_operation(operation))

        self._last_operation = self._build_operation(raw_operations[-1])

    def _build_operation(self, string):
        if '[' in string:
            value = string.strip('[]')
            return self.LookupOperation(value)
        elif '(' in string:
            function_name, function_arguments = string.strip(')').split('(')
            return self.FunctionOperation(function_name,function_arguments)
        else:
            return self.AttributeOperation(string)

    class AttributeOperation(object):
        def __init__(self, name):
            self.name = name

        def read(self, namespace, create):
            try:
                return namespace.read_attribute(self.name)
            except RookAttributeNotFound as exc:
                if create:
                    namespace.write_attribute(self.name, ContainerNamespace({}))
                    return namespace.read_attribute(self.name)
                else:
                    raise

        def write(self, namespace, value):
            return namespace.write_attribute(self.name, value)

    class LookupOperation:
        def __init__(self, name):
            if name.startswith("'"):
                self.name = name.strip("'")
            elif name.startswith('"'):
                self.name = name.strip('"')
            else:
                self.name = int(name)

        def read(self, namespace, create):
            return namespace.read_key(self.name)

        def write(self, namespace, value):
            raise RookOperationReadOnly(type(self))

    class FunctionOperation:
        def __init__(self, function_name, function_arguments):
            self.function_name = function_name
            self.function_arguments = function_arguments

        def read(self, namespace, create):
            return namespace.call_method(self.function_name, self.function_arguments)

        def write(self, namespace, value):
            raise RookOperationReadOnly(type(self))
