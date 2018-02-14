class PatternCompileError(ValueError):
    pass


class PatternNotCompiledError(ValueError):
    pass


class PatternTextTypeMismatchError(TypeError):
    def __init__(self, pattern_type, text_type):
        super().__init__(
            "Pattern of type {!r} can not match text of type {!r}".format(pattern_type.__name__, text_type.__name__)
        )


class DuplicateMatcherRegistrationError(ValueError):
    def __init__(self, name):
        super().__init__("Attempted o register a duplicate matcher {!r}".format(name))


class NoSuchMatcherError(LookupError):
    pass


class NoMatchersAvailable(ValueError):
    pass
