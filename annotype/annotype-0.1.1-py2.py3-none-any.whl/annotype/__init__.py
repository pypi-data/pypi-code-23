from functools import wraps
from inspect import isclass, signature
from marshmallow import (
    Schema,
    fields
)


def annotyped():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args = []
            new_kwargs = {}

            for param in signature(func).parameters.values():
                annon = func.__annotations__.get(param.name)

                if _param_is_positionnal(param):
                    try:
                        value = args[len(new_args)]
                    except IndexError:
                        value = kwargs[param.name]
                    finally:
                        new_args.append(validate_value(value, annon))

                elif _param_is_keyword(param):
                    try:
                        value = kwargs[param.name]
                    except KeyError:
                        pass
                    else:
                        new_kwargs[param.name] = validate_value(value, annon)

            return func(*new_args, **new_kwargs)
        return wrapper
    return decorator


def validate_value(value, target):
    if target is None:
        return value

    if isclass(target) and issubclass(target, Schema):
        value = target().load(value)
    elif isinstance(target, fields.Field):
        value = target.deserialize(value)
    return value


def _param_is_positionnal(param):
    return (
        param.kind == param.POSITIONAL_OR_KEYWORD and
        param.default is param.empty
    )


def _param_is_keyword(param):
    return (
        param.kind == param.POSITIONAL_OR_KEYWORD and
        param.default is not param.empty
    ) or param.kind == param.KEYWORD_ONLY
