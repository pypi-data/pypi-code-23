# encoding: utf-8

import warnings
import functools
import traceback


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        (filename, line_no, func_name, text) = traceback.extract_stack(limit=2)[0]

        if filename != func.__code__.co_filename or line_no != func.__code__.co_firstlineno + 1:
            root = (u' in {filename}:{line_no}'
                    .format(filename=func.__code__.co_filename,
                            line_no=func.__code__.co_firstlineno + 1))
        else:
            root = u''

        warnings.warn_explicit(
            message=(u'Call to deprecated function "{func_name}"{root}'
                     .format(func_name=func.__name__,
                             root=root)),
            category=DeprecationWarning,
            filename=filename,
            lineno=line_no)

        return func(*args, **kwargs)

    return new_func
