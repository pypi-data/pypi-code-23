# coding=utf-8
"""
Config property
"""

from .config import BaseConfig


class ConfigProp:
    """
    Decorator-class to create properties for META instances.
    """

    def __init__(self, parser: object, default: object = 'NO_DEFAULT', namespace: str = None):
        """
        Initialize properties of the descriptor.

        :param default: default value of the property if it isn't set yet
        :param parser:
        """
        self.default = default
        self.parser = parser
        self.namespace = namespace

    def _value(self, instance):
        return getattr(instance, '_config')(
            self.name,
            default=self.default,
            parser=self.parser,
            namespace=self.namespace
        )

    def _default(self, instance):
        return getattr(instance, '_config')(
            self.name,
            parser=self.parser,
            namespace=self.namespace
        )

    def __get__(self, instance, owner=None):
        """
        Retrieves value.

        If instance is None, returns the descriptor object to allow access to "default" and "type"

        If instance is a valid Config object, returns value from it

        :param instance: instance of AbstractMeta
        :param owner: actual Class of the META instance
        :return: value of this DESCRIPTOR (DEFAULT if it isn't defined)
        """

        # raise FileNotFoundError()
        if instance is None:
            # Calling from Class object
            return self

        if not isinstance(instance, BaseConfig):
            raise TypeError('_ConfigProp can only be used with EverettConfig() instances')

        if self.default == 'NO_DEFAULT':
            return self._default(instance)

        return self._value(instance)

    # pylint: disable=attribute-defined-outside-init
    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name
