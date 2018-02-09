import typing
import threading

from ioccontainer import scopes, exceptions
from ioccontainer.provider import Provider


class Container:
    def __init__(self):
        self._providers = {}
        self._singletons = {}

    def provide(self, name: typing.Union[str, typing.Type],
                closure: typing.Callable, scope=scopes.NO_SCOPE,
                override=False) -> 'Container':
        name = _get_service_name(name)
        if name in self._providers and not override:
            raise exceptions.ProviderError('Provider already exists', name)
        closure = Provider(closure, scope)
        self._providers[name] = closure
        return self

    def singleton(self, name: typing.Union[str, typing.Type],
                  closure: typing.Callable,
                  override=False) -> 'Container':
        return self.provide(name, closure, scopes.SINGLETON, override)

    def thread(self, name: typing.Union[str, typing.Type],
               closure: typing.Callable,
               override=False) -> 'Container':
        return self.provide(name, closure, scopes.THREAD, override)

    def get(self, name: typing.Union[str, typing.Type]) -> typing.Any:
        name = _get_service_name(name)
        if name not in self._providers:
            raise exceptions.ProviderError('Provider does not exist', name)
        p = self._providers[name]
        if p.scope is scopes.NO_SCOPE:
            return p()
        if p.scope is scopes.SINGLETON:
            if name not in self._singletons:
                self._singletons[name] = p()
            return self._singletons[name]
        if p.scope is scopes.THREAD:
            thread_storage = threading.local()
            if not hasattr(thread_storage, name):
                setattr(thread_storage, name, p())
            return getattr(thread_storage, name)
        raise exceptions.ScopeError('Unhandled scope', p.scope)


def _get_service_name(cls: typing.Type) -> str:
    if isinstance(cls, str):
        return cls
    try:
        return '.'.join([cls.__module__, cls.__name__])
    except AttributeError:
        raise exceptions.ProviderError('Invalid service name', cls)
