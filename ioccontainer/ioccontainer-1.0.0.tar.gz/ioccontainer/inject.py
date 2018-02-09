import inspect
import typing

from ioccontainer import exceptions

if typing.TYPE_CHECKING:
    from ioccontainer.container import Container


def inject_decorator(container: 'Container'):
    class InjectDecorator(object):
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
            if not _parameter_injection_requested(parameter, self.inject_args,
                                                  self.inject_kwargs):
                return new_args, kwargs

            if _default_parameter_provided(parameter):
                raise exceptions.ParameterError(
                    'A default parameter has been provided',
                    parameter.name
                )

            if _argument_provided(position, parameter, new_args, kwargs):
                return new_args, kwargs

            cls = _get_parameter_class(parameter, self.inject_kwargs)
            service = container.get(cls)

            if _is_positional_argument(position, parameter, new_args):
                new_args.append(service)
            elif _is_keyword_argument(parameter):
                kwargs[parameter.name] = service
            else:
                raise exceptions.ParameterError(
                    'Unhandled injection parameter',
                    parameter.name)

            return new_args, kwargs

    return InjectDecorator


def _parameter_injection_requested(parameter: inspect.Parameter,
                                   inject_args: typing.Tuple,
                                   inject_kwargs: typing.Dict) -> bool:
    if parameter.name in inject_args:
        return True
    if parameter.name in inject_kwargs.keys():
        return True
    return False


def _get_parameter_class(parameter: inspect.Parameter,
                         inject_kwargs: typing.Dict) -> str:
    cls = inject_kwargs.get(parameter.name, None)
    if cls is None:
        cls = parameter.annotation

    if cls is inspect.Parameter.empty:
        # Don't know which service to retrieve from the container.
        raise exceptions.ParameterError('No service specified',
                                        parameter.name)
    return cls


def _default_parameter_provided(parameter: inspect.Parameter) -> bool:
    if parameter.default is inspect.Parameter.empty:
        return False
    if parameter.default is not None:
        return False
    return True


def _argument_provided(position: int, parameter: inspect.Parameter,
                       args: typing.List, kwargs: typing.Dict) -> bool:
    return position < len(args) or parameter.name in kwargs.keys()


def _is_positional_argument(
        position: int, parameter: inspect.Parameter,
        args: typing.List) -> bool:
    positional_types = (inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD)
    if parameter.kind not in positional_types:
        return False
    return position == len(args)


def _is_keyword_argument(parameter: inspect.Parameter) -> bool:
    keyword_types = (inspect.Parameter.KEYWORD_ONLY,
                     inspect.Parameter.POSITIONAL_OR_KEYWORD)
    return parameter.kind in keyword_types
