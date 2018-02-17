""" Classes and functions for code support (including tests)
"""


class Bunch(object):
    """ Class to represent dictionary as object

    Almost any key is allowed, but we drop keys beginning with ``__``, and
    raise an error for keys beginning with ``bunch_``.
    """
    def __init__(self, dict_like):
        """ Initialize Bunch

        Parameters
        ----------
        dict_like : object
            Object implementing `items` method - for example, a ``dict``.
        """
        self.bunch_update(dict_like)

    def bunch_update(self, dict_like):
        """ Update object attributes from `dict_like`

        Almost any key is allowed, but we drop keys beginning with ``__``, and
        raise an error for keys beginning with ``bunch_``.

        Parameters
        ----------
        dict_like : object
            Object implementing `items` method - for example, a ``dict``.
        """
        for key, name in dict_like.items():
            if key.startswith('__'):
                continue
            if key.startswith('bunch_'):
                raise ValueError(
                    'Dict key {} conflicts with Bunch API'.format(key))
            self.__dict__[key] = name


def read_file(fname):
    """ Read file at `fname` as text, return `contents`

    Parameters
    ----------
    fname : str
        Filename.

    Returns
    -------
    contents : str
        Contents read from `fname`.
    """
    with open(fname, 'rt') as fobj:
        contents = fobj.read()
    return contents
