import typing
import inspect
import threading

NO_SCOPE = 0
SINGLETON = 1
THREAD = 2
SCOPES = (NO_SCOPE, SINGLETON, THREAD)


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


class Container:
    def __init__(self):
        self._providers = {}
        self._singletons = {}

    def provide(self, name: typing.Union[str, typing.Type],
                closure: typing.Union[typing.Callable, 'Provider'],
                scope=NO_SCOPE, override=False) -> 'Container':
        name = _get_service_name(name)
        if name in self._providers and not override:
            raise ProviderError('Provider already exists', name)
        if not isinstance(closure, Provider):
            closure = Provider(closure, scope)
        self._providers[name] = closure
        return self

    def singleton(self, name: typing.Union[str, typing.Type],
                  closure: typing.Union[typing.Callable, 'Provider'],
                  override=False) -> 'Container':
        return self.provide(name, closure, SINGLETON, override)

    def thread(self, name: typing.Union[str, typing.Type],
               closure: typing.Union[typing.Callable, 'Provider'],
               override=False) -> 'Container':
        return self.provide(name, closure, THREAD, override)

    def get(self, name: typing.Union[str, typing.Type]) -> typing.Any:
        name = _get_service_name(name)
        if name not in self._providers:
            raise ProviderError('Nonexistent provider', name)
        p = self._providers[name]
        if p.scope is NO_SCOPE:
            return p()
        if p.scope is SINGLETON:
            if name not in self._singletons:
                self._singletons[name] = p()
            return self._singletons[name]
        if p.scope is THREAD:
            thread_storage = threading.local()
            if not hasattr(thread_storage, name):
                setattr(thread_storage, name, p())
            return getattr(thread_storage, name)
        raise ScopeError('Unhandled scope', p.scope)


class Provider:
    def __init__(self, closure: typing.Callable, scope: int):
        if scope not in SCOPES:
            raise ScopeError('Invalid scope', scope)
        self.closure = closure
        self.scope = scope

    def __call__(self) -> typing.Any:
        return self.closure()


def _get_service_name(cls: typing.Type) -> str:
    if isinstance(cls, str):
        return cls
    try:
        return '.'.join([cls.__module__, cls.__name__])
    except AttributeError:
        raise ProviderError('Invalid service name', cls)


class InjectorDecorator(object):
    def __init__(self, *args: typing.Tuple, **kwargs: typing.Dict):
        self.inject_args = args
        self.inject_kwargs = kwargs

    def __call__(self, f: typing.Callable) -> typing.Callable:
        def wrapped_f(*args: typing.Tuple, **kwargs: typing.Dict):
            new_args = list(args)
            parameters = [parameter[1] for parameter in
                          inspect.signature(f).parameters.items()]
            for i, parameter in enumerate(parameters):
                new_args, kwargs = self.process_parameter(
                    i, parameter, new_args, kwargs
                )

            return f(*new_args, **kwargs)

        return wrapped_f

    def process_parameter(
            self, position: int, parameter: inspect.Parameter,
            new_args: typing.List, kwargs: typing.Dict
    ) -> typing.Tuple[typing.List, typing.Dict]:
        if not self._parameter_injection_requested(parameter):
            return new_args, kwargs

        if self._default_parameter_provided(parameter):
            raise ParameterError('A default parameter has been provided',
                                 parameter.name)

        if self._argument_provided(position, parameter, new_args, kwargs):
            return new_args, kwargs

        cls = self._get_parameter_class(parameter, self.inject_kwargs)
        service = container.get(cls)

        if self._is_positional_argument(position, parameter, new_args):
            new_args.append(service)
        elif self._is_keyword_argument(parameter):
            kwargs[parameter.name] = service
        else:
            raise ParameterError('Unhandled injection parameter',
                                 parameter.name)

        return new_args, kwargs

    def _parameter_injection_requested(
            self,
            parameter: inspect.Parameter
    ) -> bool:
        if parameter.name in self.inject_args:
            return True
        if parameter.name in self.inject_kwargs.keys():
            return True
        return False

    @staticmethod
    def _get_parameter_class(parameter: inspect.Parameter,
                             inject_kwargs: typing.Dict) -> str:
        cls = inject_kwargs.get(parameter.name, None)
        if cls is None:
            cls = parameter.annotation

        if cls is inspect.Parameter.empty:
            # Don't know which service to retrieve from the container.
            raise ParameterError('No service specified', parameter.name)
        return cls

    @staticmethod
    def _default_parameter_provided(parameter: inspect.Parameter) -> bool:
        if parameter.default is inspect.Parameter.empty:
            return False
        if parameter.default is not None:
            return False
        return True

    @staticmethod
    def _argument_provided(position: int, parameter: inspect.Parameter,
                           args: typing.List, kwargs: typing.Dict) -> bool:
        return position < len(args) or parameter.name in kwargs.keys()

    @staticmethod
    def _is_positional_argument(position: int, parameter: inspect.Parameter,
                                args: typing.List) -> bool:
        positional_types = (inspect.Parameter.POSITIONAL_ONLY,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD)
        if parameter.kind not in positional_types:
            return False
        return position == len(args)

    @staticmethod
    def _is_keyword_argument(parameter: inspect.Parameter) -> bool:
        keyword_types = (inspect.Parameter.KEYWORD_ONLY,
                         inspect.Parameter.POSITIONAL_OR_KEYWORD)
        return parameter.kind in keyword_types


class ProviderDecorator(object):
    def __init__(self, name: typing.Union[str, typing.Type],
                 scope: int = NO_SCOPE, override: bool = False):
        self.name = name
        self.scope = scope
        self.override = override

    def __call__(self, f: typing.Callable) -> typing.Callable:
        container.provide(self.name, f, self.scope, self.override)
        return f


container = Container()
inject = InjectorDecorator
provider = ProviderDecorator
