def coalesce( value, default_ ):
    """
    The null-coalescing operator, which is strangely missing from Python.
    """
    if value is None:
        return default_
    else:
        return value
