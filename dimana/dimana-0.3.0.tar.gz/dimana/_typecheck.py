def typecheck(obj, expectedtype):
    if not isinstance(obj, expectedtype):
        raise TypeError(
            'Expected {!r}, found {!r}'
            .format(
                expectedtype.__name__,
                type(obj).__name__,
            )
        )
