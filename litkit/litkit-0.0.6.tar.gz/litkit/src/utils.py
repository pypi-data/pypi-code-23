import inspect
from typing import List

import pandas as pd


def get_args(fn, args, kwargs, ignore: List) -> List:
    signature = inspect.signature(fn)

    sig_parameters = list(signature.parameters.items())

    if sig_parameters[0][0] == "self":
        args = args[1:]
        sig_parameters = sig_parameters[1:]

    parameters = []
    for p in sig_parameters:
        parameters.append([p[0], None])

    for i, a in enumerate(args):
        parameters[i][1] = a

    for i, _ in enumerate(parameters):
        key = parameters[i][0]
        if key in kwargs:
            parameters[i][1] = kwargs[key]

    for i, p in enumerate(parameters):
        if p[0] in ignore:
            del parameters[i]

    return parameters


def serialize_call(fn, args, kwargs, ignore: List) -> str:
    parameters = get_args(fn, args, kwargs, ignore)

    serialized = fn.__module__ + "." + fn.__name__ + '('
    for p in parameters:
        if isinstance(p[1], List):
            s = "["
            for i in p[1]:
                s += str(i) + ","

            s += "]"

            serialized += str(p[0]) + ":" + s + " "

            continue

        if isinstance(p[1], pd.DataFrame):
            vs = p[1].values

            s = ''
            for v in vs:
                s += str(max(v)) + str(min(v))

            serialized += str(p[0]) + ":" + s + " " + ','.join(list(p[1].columns))

            continue

        if hasattr(p[1], "__dict__"):
            p[1] = "{" + "".join("{}:{},".format(key, val) for key, val in sorted(p[1].__dict__.items()))
            p[1] = p[1][:-1] + "}"

            serialized += str(p[0]) + ":" + str(p[1]) + " "

        serialized += str(p[0]) + ":" + str(p[1]) + " "

    serialized = serialized[:-1] + ")"

    serialized = serialized.replace("/", "")

    return serialized


def get_arg(fn, args, kwargs, arg: str):
    args = get_args(fn, args, kwargs, [])

    return list(filter(lambda a: a[0] == arg, args))[0][1]
