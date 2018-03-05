"""Exception utils."""


def raise_truthy(d, k, exception=None):
    """Raises exception if value is truthy.

    Parameters
    ----------
    d : dict
    k : str
    exception : Exception, optional

    Returns
    -------
    None

    Raises
    ------
    ValueError
        When dict value is truthy and a custom exception is not passed.

    """
    val = d.get(k)
    if (val):
        raise exception or ValueError(k)
    return val


def raise_falsey(d, k, exception=None):
    """Return value from dict if truthy, raises otherwise.

    If an exception is provided, it will be the exception raised.

    Parameters
    ----------
    d : dict
    k : str
    exception : Exception, optional

    returns
    -------
    any
        Returns the dict value

    Raises
    ------
    ValueError
        When dict value is falsey and a custom exception is not passed.

    """
    val = d.get(k)
    if not val:
        raise exception or ValueError(k)
    return val


def raise_none(d, k, exception=None):
    """Return value from dict if not None, raises otherwise.

    If an exception is provided, it will be the exception raised.

    Parameters
    ----------
    d : dict
    k : str
    exception : Exception, optional

    returns
    -------
    any
        Returns the dict value

    Raises
    ------
    ValueError
        When dict value is falsey and a custom exception is not passed.

    """
    val = d.get(k)
    if val is None:
        raise exception or ValueError(k)
    return val
