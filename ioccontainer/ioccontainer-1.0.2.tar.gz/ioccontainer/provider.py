import typing

from ioccontainer import scopes, exceptions

if typing.TYPE_CHECKING:
    from ioccontainer.container import Container


class Provider:
    def __init__(self, closure: typing.Callable, scope: int):
        if scope not in scopes.SCOPES:
            raise exceptions.ScopeError('Invalid scope', scope)
        self.closure = closure
        self.scope = scope

    def __call__(self) -> typing.Any:
        return self.closure()


def provider_decorator(container: 'Container'):
    class ProviderDecorator(object):
        def __init__(self, name: typing.Union[str, typing.Type],
                     scope: int = scopes.NO_SCOPE, override: bool = False):
            self.name = name
            self.scope = scope
            self.override = override

        def __call__(self, f: typing.Callable) -> typing.Callable:
            container.provide(self.name, f, self.scope, self.override)
            return f

    return ProviderDecorator
