from attrdict import AttrMap
import re


class InfoDict(object):
    """Read-only informational dictionary with attribute access.

    Parameters
    ----------
    dct : dict
        The dictionary to initialize values with.
    """
    def __init__(self, dct):
        for e in dct:
            if not valid_attrname(e):
                raise AttributeError("Invalid attribute name: '%s'" % str(e))
        super().__setattr__('__dict__', dct)

    def get(self, key, default=None):
        """Get the corresponding value to the given key. If not found, returns None.

        Parameters
        ----------
        key : string
           The key to get the value for.
        default : object, optional
           The default value to return if the key is invalid. Defaults to None.

        Returns
        -------
        value : object
           The corresponding value to the key.
        """
        if key not in self.__dict__:
            return default
        return self.__dict__[key]

    def __getattr__(self, key):
        """Returns None if the attribute does not exist."""
        if key not in self.__dict__:
            return None
        return self.__dict__[key]

    def __setattr__(self, key, value):
        """Disallows setting of attributes."""
        raise AttributeError("'%s' object can not set attributes." % str(cls))

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Arguments(InfoDict):
    """Represents arguments with their values."""
    def __init__(self, dct):
        d = {}
        for arg in dct:
            if not valid_arg(arg):
                raise AttributeError("Invalid argument name: '%s'" % arg)
            d[to_var(arg)] = dct[arg]
        super().__init__(d)

    def get(self, key, default=None):
        key = to_var(key)
        return super.get(key, default)

    def __str__(self):
        dct = {}
        d = self.__dict__
        for e in d:
            dct[to_arg(e)] = d[e]
        return str(dct)


class MetaData(InfoDict):
    """Represents metadata sent with a message.

    Parameters
    ----------
    author : object
        The user who called the command.
    location : object
        The location where the command was called.
    custom: InfoDict, optional
        Platform-specific data.
    """
    def __init__(self, author, location, custom=None):
        super().__init__(dict(author=author, location=location, custom=custom))


def valid_attrname(attr):
    p = r'^[^0-9][0-9a-zA-Z_]+$'
    return bool(re.search(p, attr))


arg_regex = r'^[^0-9][0-9a-zA-Z-]+$'
def valid_arg(arg):
    return bool(re.search(arg_regex, arg))


def to_var(arg):
    return arg.replace('-', '_')


def to_arg(arg):
    return arg.replace('_', '-')


def match_command(message, command, metadata, eventloop=None):
    """Attempts to match the message to the given command.

    Parameters
    ----------
    message : str
        The message to match against.
    command : monika.core.command or monika.core.namespace
        The command to match against.
    eventloop : asyncio.eventloop, optional
        The event loop to sync to.
    """
    matched_command = None
    args = dict(command.args)
    if eventloop is None:
        eventloop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(matched_func(args, metadata), eventloop)
