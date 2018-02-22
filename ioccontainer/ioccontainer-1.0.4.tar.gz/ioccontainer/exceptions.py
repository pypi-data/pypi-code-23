class IocError(Exception):
    pass


class ProviderError(IocError):
    def __init__(self, message, name):
        self.message = message
        self.name = name


class ScopeError(IocError):
    def __init__(self, message, scope):
        self.message = message
        self.scope = scope


class ParameterError(IocError):
    def __init__(self, message, scope):
        self.message = message
        self.scope = scope
