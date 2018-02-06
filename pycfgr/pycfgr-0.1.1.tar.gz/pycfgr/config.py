"""`pycfgr` config reader class"""

import os
import re
from collections import Mapping
from pycfgr.readers import READERS


class Config(dict):
    """`pycfgr` config reader class.

    It supports multiple settings with possible inheritance.
    The class inherits from the `dict` class,
    so it supports all methods like `get`, `pop` or `items`.
    Values within config can be interpolated based on other values.
    """

    def __init__(self, config='config.yml', mode='default',
                 reader='yaml', use_parent=True, sep="."):
        """Initilization method.

        Parameters
        ----------
        config : str or dict
            Name of the config file or a `dict` representing it.
            If name is given and it is not found in the current location,
            then parent directories are searched.
        mode : str
            Mode of the config to read in.
            All modes other than 'default' inherits from the 'default' config.
            Inheritance is specified via 'config_inheritance'
            field in the config.
            It should specify a single mode (or a list of modes)
            that the given mode inherits from.
            Lists of modes have to be sorted by decreasing importance.
            Default mode can not inherit from any other mode
            (even if it has `config_inheritance` field).
        reader : str or callable
            Name of a reader method [ yaml(yml) / json ]
            or an arbitrary reader function.
        use_parent : bool
            Should parent directories be searched
            if config is not found in the path.
        """
        # Determine reader
        assert isinstance(reader, str) or callable(reader), \
            "`reader` has to be a string [yaml / yml / json] or a reading function."
        if isinstance(reader, str):
            try:
                reader = READERS[reader]
            except KeyError:
                raise ValueError("Not supported reader name: %s." % reader)
        self.reader = reader
        # Set up regex for extracting and removing paths
        self.rx = re.compile(r"\{([a-z"+re.escape(sep)+r"]*)\}", re.IGNORECASE)
        # Read configuration
        if not isinstance(config, Mapping):
            path = self._find_path(config, use_parent)
            config = self._read_config(path, mode)
        super().__init__(config)
        # Interpolate values
        self.sep = sep
        self = self._interpolate_values(self)

    def __repr__(self):
        """String representation."""
        return "Config({})".format(super().__repr__())

    def _find_path(self, path, use_parent):
        """Find the path to a config."""
        dirpath = os.path.dirname(os.path.realpath(path))
        config = os.path.basename(path)
        if os.path.exists(path):
            return path
        elif use_parent:
            dirpath = os.path.join(dirpath, '..')
            path = os.path.join(dirpath, config)
            try:
                return self._find_path(path, use_parent)
            except RuntimeError as runerr:
                if runerr.args[0] != "maximum recursion depth exceeded":
                    raise
                else:
                    raise RecursionError(
                        "Could not find `{}` in parent directories.".format(config)
                    )
        else:
            raise ValueError("`{}` does not exist.".format(path))

    def _read_config(self, path, mode='default'):
        """Read a config from a `.yaml` file."""

        def merge(src, dest):
            """Merge two dicts recursively."""
            src, dest = src.copy(), dest.copy()
            for key, value in dest.items():
                if isinstance(value, Mapping):
                    if isinstance(src.get(key, {}), Mapping):
                        src[key] = merge(src.get(key, {}), value)
                    else:
                        src[key] = value
                else:
                    src[key] = value
            return src

        with open(path, 'r') as stream:
            config = self.reader(stream)
        if 'default' in config:
            if mode in config:
                cfg = config[mode]
            else:
                raise ValueError("Mode `{}` not defined in the config.".format(mode))
            if mode != 'default':
                inheritance = cfg.get('_inherits', [])
                cfg = merge(config['default'], cfg)
                for name in reversed(inheritance):
                    cfg = merge(config[name], cfg)
        else:
            cfg = config
        return cfg

    def _interpolate(self, value):
        """Interpolate value."""
        match = self.rx.search(value) if isinstance(value, str) else None
        if match:
            subs = [ self.pick(m.group(1)) for m in self.rx.finditer(value) ]
            # If there is only one substitution and no more text
            if len(subs) == 1 and match.start() == 0 and match.end() == len(value):
                # then the original value is used instead of its string representation
                return subs[0]
            value = self.rx.sub(r"{}", value)
            value = value.format(*subs)
        return value

    def _interpolate_values(self, data):
        """Interpolate values in the config."""
        for key, value in data.items():
            if isinstance(value, Mapping):
                data[key] = self._interpolate_values(value)
            elif isinstance(value, (list, tuple)):
                data[key] = [ self._interpolate(x) for x in data[key] ]
            else:
                data[key] = self._interpolate(value)
        return data

    def pick(self, path):
        """Get config value using path.

        Parameters
        ----------
        path : str
            Path specifying element to look for.
            Must use the `sep` attribute.
        """
        keys = path.split(self.sep)
        current_keys = []
        val = self.copy()
        for key in keys:
            current_keys.append(key)
            try:
                val = val[key]
            except KeyError:
                raise KeyError("Can not find key `{}` at path `{}`".format(
                    key, self.sep.join(current_keys)
                ))
        return val

    def get(self, *args):
        """Get config value.

        Parameters
        ----------
        *args :
            field names to look for. Subsequent names
            are treated as nested names.
        """
        return self.pick(self.sep.join(args))
