from string import Formatter

if "rook" in __name__:
    # This is caused by not changing sys.path in Rook combined with the way we package the code
    from rook.lib.logger import logger
else:
    from lib.logger import logger

from ..namespaces.formatted_namespace import FormattedNamespace

from ..namespaces.container_namespace import ContainerNamespace


class Format(object):

    class NamespaceFormatter(Formatter):

        def __init__(self, namespace, factory, *args, **kwargs):
            super(Format.NamespaceFormatter, self).__init__(*args, **kwargs)

            self.namespace = namespace
            self.factory = factory

        def get_field(self, field_name, args, kwargs):
            try:
                path = self.factory.get_path(field_name)
                value = path.read_from(self.namespace)
                return value.obj, False
            except Exception:
                logger.exception('Failed to read value- %s', field_name)
                return '<Missing>', False

    def __init__(self, arguments, factory):
        self.factory = factory

        self._format = arguments['format']
        self._target = factory.get_path(arguments['path'])

        self._paths = list()
        if 'values' in arguments:
            for item in arguments['values']:
                self._paths.append(factory.get_path(item))

    def execute(self, namespace):
        values = []
        for path in self._paths:
            values.append(path.read_from(namespace).obj)

        if values:
            formatter = Formatter()
        else:
            formatter = self.NamespaceFormatter(namespace, self.factory)

        message = formatter.vformat(self._format, values, {})

        self._target.write_to(namespace, FormattedNamespace(message))
