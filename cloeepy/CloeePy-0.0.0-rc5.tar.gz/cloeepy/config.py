import os
import sys
import yaml

class obj(object):
    """
    Special class, that when instantited, recursively turns the provided dictionary
    into instance attributes.

    Thus, a dictionary schema like this

    d = {
        "a" : "b",
        "c" : "d",
        "e" : {
            "f" : "g",
            "h" : "i",
            "j" : ["k", "l", "m"],
        },
    }

    becomes an object where:

    d.a -> "b"
    d.e.j -> ["k", "l", "m"]
    """
    def __init__(self, d: dict):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)

class Config(object):
    """
    Config Class reads YAML configuration files and turns them into Python
    dictionary representation and nested object representation.
    """

    def __init__(self):
        self._set_config_path()
        self._load_config()
        self._set_attributes()

    def _set_config_path(self):
        """
        Reads config path from environment variable CLOEEPY_CONFIG_PATH
        and sets as instance attr
        """
        self._path = os.getenv("CLOEEPY_CONFIG_PATH")
        if self._path is None:
            msg = "CLOEEPY_CONFIG_PATH is not set. Exiting..."
            sys.exit(msg)


    def _load_config(self):
        """
        Loads the YAML configuration file and sets python dictionary and raw contents
        as instance attrs.
        """
        if not os.path.exists(self._path):
            sys.exit("Config path %s does not exist" % self._path)
        # create empty config object
        self._config_dict = {}
        # read file and marshal yaml
        with open(self._path, 'r') as f:
            self._raw = f.read()
            self._config_dict = yaml.load(self._raw)


    def as_dict(self):
        """
        Accessor method that returns configuration as a dictionary
        """
        return self._config_dict

    def get_path(self):
        """
        Returns path to config file
        """
        return self._path

    def _set_attributes(self):
        """
        Recursively transforms config dictionaries into instance attrs to make
        for easy dot attribute access instead of dictionary access.
        """
        # turn config dict into nested objects
        config = obj(self._config_dict)
        # set the attributes onto instance
        for k, v in self._config_dict.items():
            setattr(self, k, getattr(config, k))
