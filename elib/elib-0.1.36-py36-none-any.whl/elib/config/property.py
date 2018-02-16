# coding=utf-8
"""
Config property
"""
# pylint: disable=too-few-public-methods

import everett.manager

from .config import BaseConfig


class _ConfigProp:
    """
    Actual descriptor object created during ConfigProp.__call___ below.

    Accessing a ConfigProp from the Config class itself (Config.PROPERTY as opposed to Config().property) gives access
    to the object itself, with "default", "type", "__doc__", "key" and "func".

    """

    def __init__(self, func: callable, default: object, parser: object, namespace):
        """
        Initialize the DESCRIPTOR.

        :param func: callable to overwrite
        :param default: default value if there's nothing in the EverettConfig yet
        :param parser: type of object allowed to be SET
        """
        self.func = func
        self.prop_name = self.func.__name__.upper()
        if namespace:
            self.prop_name = self.prop_name.replace(
                namespace.upper() + '_', '')
        if not isinstance(default, str):
            default = str(default)
        self.default = default
        if parser is bool:
            parser = everett.manager.parse_bool
        self.parser = parser
        self.__doc__ = func.__doc__
        self.namespace = namespace

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
            raise TypeError(
                '_ConfigProp can only be used with EverettConfig() instances')
        if self.default == 'NO_DEFAULT':
            return getattr(instance, '_config')(
                self.prop_name,
                parser=self.parser,
                namespace=self.namespace
            )

        return getattr(instance, '_config')(
            self.prop_name,
            default=self.default,
            parser=self.parser,
            namespace=self.namespace
        )


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
        self.type = parser
        self.namespace = namespace

    def __call__(self, func: callable) -> _ConfigProp:
        """
        Creates a DESCRIPTOR instance for a method of a META instance.

        :param func: function to decorate
        :return: decorated function as a descriptor instance of _MetaProperty
        :rtype: _MetaProperty
        """
        return _ConfigProp(func, self.default, self.type, self.namespace)
