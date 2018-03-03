"""
Every connection should inherit from the Base. Base class is a Singleton class factory for all of the inherited subclass.
"""
import logging
from typing import Type, TypeVar, List, Dict

from ..config import Config

B = TypeVar('T', bound='Base')


class Base:
    """
    Mother of all of the connection. It's implement methods for creating itself.
    All of the created instance is stored in the __connection_pool class variable by the given name.
    """
    __connection_pool = {}
    logger = logging.getLogger(__name__)

    def __new__(cls: Type[B], name: str, *args, **kwargs) -> B:  # pylint: disable=unused-argument
        """
        Override object creation with implementing Singleton pattern.
        Args:
            name(str): name of the object. It will index by this name.
            *args:
            **kwargs:

        Returns:
            If no instance exists with this name than a new object otherwise an already created object with the name.
        """
        if Base.__connection_pool.get(name, None) is None:
            Base.__connection_pool[name] = object.__new__(cls)
            Base.name = name
            Base.logger.info("%s connection initialized", name)
        return Base.__connection_pool[name]

    def __init__(self, name: str, *args, **kwargs):
        """
        Regular __init__ method...
        Args:
            name(str): name of the object
            *args:
            **kwargs:
        """
        self.name = name

    @classmethod
    def get_instance(cls: Type[B], name: str, *args, **kwargs) -> B:
        """
        Getter class method for the class. It returns an object if exist or create a new. Every parameter will be pass to the created class.
        Args:
            name(str): name of the object
            *args:
            **kwargs:

        Returns:
            Returns an instance of the class.
        """
        if cls.__connection_pool.get(name, None) is None:
            cls.create_instance(name=name, *args, **kwargs)
        return cls.__connection_pool[name]

    @classmethod
    def create_instance(cls: Type[B], name: str, *args, **kwargs) -> B:
        """
        Instance creator class method for the class, it creates itself. Every parameter will be pass to the created class.
        Args:
            name(str): name of the object
            *args:
            **kwargs:

        Returns:
            Returns an instance of the class.
        """
        return cls(name=name, *args, **kwargs)

    @classmethod
    def create_instances(cls: Type[B], name, *args, **kwargs) -> List[B]:
        """
        Create all of the instances based on the configuration file.
        For the Base class it's just a wrapper over create_instance() method for supporting multi connection creation from one connection.
        Returns:
            List of created instances.
        """
        return [cls.create_instance(name=name, *args, **kwargs)]


def create_connections() -> Dict[str, B]:
    """
    Call create_instances() on all of the subclasses of Base.
    Returns:
        Dict of connections
    """
    lookup_table = _get_all_connection_class()
    config = Config().connections_as_list
    instances = {}

    for connection_config in config:
        instances[connection_config['type']] = lookup_table[connection_config['type']].create_instances(**connection_config)
    return instances


def _get_all_connection_class() -> dict:
    subclasses = [globals()['Base']]

    def all_subclasses(cls):
        return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]

    subclasses.extend(all_subclasses(globals()['Base']))
    lookup_table = {str(cls.__name__).lower(): cls for cls in subclasses}
    return lookup_table
