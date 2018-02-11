import collections
import typing
import argparse


__version__ = '0.0.1'


class TypedArgumentParser(argparse.ArgumentParser):

    def __init__(self, func, **kwargs):
        super(TypedArgumentParser, self).__init__(**kwargs)

        annotations = func.__annotations__
        arg_names = func.__code__.co_varnames
        default_values = func.__defaults__

        if default_values:
            n_positional = len(arg_names) - len(default_values)
        else:
            n_positional = len(arg_names)

        for i, name in enumerate(arg_names):
            if name in annotations:
                annotation = annotations[name]
            else:
                annotation = str

            if i >= n_positional:
                optional = True
                default = default_values[i-n_positional]
            else:
                optional = False
                default = None

            self._add_typed_params(name, annotation, optional, default)

    def _add_typed_params(self, name, annotation, optional, default):
        param = {}

        if optional:
            name = '--' + name

        if annotation == bool:
            if not optional:
                name = "--" + name

            if not optional or default is False:
                param['action'] = 'store_true'
            else:
                param['action'] = 'store_false'

        elif _is_variable_length_type(annotation):
            param['type'] = annotation.__args__[0]
            param['nargs'] = '*'
            param['default'] = default

        else:
            param['type'] = annotation
            param['action'] = 'store'
            param['default'] = default

        self.add_argument(name, **param)


def _is_variable_length_type(t):
    # __origin__ attributes of typing objects differ between python versions.
    variable_length_origins = [
        list,                          # List     >=3.7
        collections.abc.Sequence,      # Sequence >=3.7
        typing.List,                   # List     <=3.6
        typing.Sequence,               # Sequence <=3.6
    ]
    return (hasattr(t, "__origin__") and
            t.__origin__ in variable_length_origins)


def execute(func):
    return func(**vars(TypedArgumentParser(func).parse_args()))
