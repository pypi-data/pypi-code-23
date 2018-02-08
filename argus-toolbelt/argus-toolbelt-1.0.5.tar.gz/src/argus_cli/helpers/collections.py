import collections
from argparse import ArgumentParser


class ImmutableDeepDict(collections.MutableMapping):
    """A dictionary with ability for deep get and set

    A key turns immutable after being set.
    """
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)

    def __getitem__(self, key):
        """Gets a plugin

        :param key: The name and hierarchy of the plugin
        :returns: The dict that holds the plugins commands
        """
        def recurse(name: tuple, parent: dict) -> dict:
            plugin_name = name[0]

            if plugin_name not in parent:
                raise KeyError("The key does not exist!")
            elif len(name) > 1:
                return recurse(name[1:], parent[plugin_name])
            else:
                return parent[plugin_name]

        if isinstance(key, str):
            key = (key,)

        return recurse(key, self._dict)

    def __setitem__(self, key, value):
        """Adds a key

        Fills missing steps with a empty dict

        :param key: The name and hierarchy of the plugin
        :returns: The dict that holds the plugins commands
        """

        def recurse(name: tuple, parent: dict) -> dict:
            plugin_name = name[0]


            if len(name) > 1:
                if plugin_name not in parent:
                    parent[plugin_name] = {}
                return recurse(name[1:], parent[plugin_name])
            elif plugin_name in parent:
                raise KeyError("The key already exists")
            else:
                parent[plugin_name] = value
                return parent[plugin_name]

        if isinstance(key, str):
            key = (key,)
        return recurse(key, self._dict)

    def __delitem__(self, key):
        del self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __str__(self):
        return str(self._dict)
