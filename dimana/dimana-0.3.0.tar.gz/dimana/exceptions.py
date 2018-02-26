class UnitsMismatch (TypeError):
    """Represents binary operations on incompatible unit dimensions."""
    def __init__(self, left, right):
        TypeError.__init__(
            self,
            '{!r} does not match {!r}'.format(str(left), str(right)),
        )


class BaseParseError (ValueError):
    def __init__(self, tmpl, *args, **kw):
        ValueError.__init__(self, tmpl.format(*args, **kw))


class UnitsParseError (BaseParseError):
    pass


class ValueParseError (BaseParseError):
    pass
