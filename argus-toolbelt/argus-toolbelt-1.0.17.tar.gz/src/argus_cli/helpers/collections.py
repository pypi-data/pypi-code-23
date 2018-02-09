import collections
from argparse import ArgumentParser


class ImmutableDeepDict(collections.MutableMapping):
    """A dictionary with ability for deep get and set

    A key turns immutable after being set.
    """
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)

    def __getitem__(self, keys):
        """Gets a plugin

        :param keys: The name and hierarchy of the plugin
        :returns: The dict that holds the plugins commands
        """
        def recurse(name: tuple, parent: dict) -> dict:
            key = name[0]

            if key not in parent:
                raise KeyError("The key does not exist!")
            elif len(name) > 1:
                return recurse(name[1:], parent[key])
            else:
                return parent[key]

        if not keys:
            raise KeyError("Key is empty")
        elif isinstance(keys, str):
            keys = (keys,)
        return recurse(keys, self._dict)

    def __setitem__(self, keys, value):
        """Adds a key

        Fills missing steps with a empty dict

        :param keys: The name and hierarchy of the plugin
        :returns: The dict that holds the plugins commands
        """

        def recurse(name: tuple, parent: dict) -> dict:
            key = name[0]



            if len(name) > 1:
                if key not in parent:
                    parent[key] = {}
                return recurse(name[1:], parent[key])
            elif key in parent:
                raise KeyError("The key already exists")
            else:
                parent[key] = value
                return parent[key]

        if not keys:
            raise KeyError("Key is empty")
        elif isinstance(keys, str):
            keys = (keys,)
        return recurse(keys, self._dict)

    def __delitem__(self, key):
        del self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __str__(self):
        return str(self._dict)
