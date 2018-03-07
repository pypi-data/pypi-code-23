from __future__ import print_function
import inspect


def smart_map(func, data):
    """Recursive map function.

    If data is iterable, it will recursively apply smart_map to all elements.
    This function attempts to keep the original class.

    :param func: function to apply on elements
    :param data: data
    :return: transformed data
    """

    if isinstance(data, str) or isinstance(data, unicode):
        # These are iterable, but we shouldn't iterate through them.
        return func(data)
    else:
        try:
            values = [smart_map(func, value) for value in data]
        except TypeError:
            values = None   # not iterable

        if values is not None:
            cname = data.__class__.__name__
            if cname == 'ndarray':
                # special case for numpy arrays
                b = data.__class__(data.shape)
                b[:] = values
                return b
            elif cname == 'generator':
                # can't create a generator like this
                return list(values)
            else:
                # create object from original class
                return data.__class__(values)
        else:
            # not iterable
            return func(data)


def get_type_name(x):
    return type(x).__name__.strip('3264_')


def detect_type(values):
    """Detect the type."""

    types = set([get_type_name(v) for v in values])

    with_none = False
    if type(None) in types:
        with_none = True
        types.remove(type(None))

    if types <= {'int', 'long'}:
        output = 'int'
    elif types <= {'int', 'long', 'float'}:
        output = 'float'
    elif types <= {'str', 'string', 'unicode'}:
        output = 'str'
    elif types <= {'datetime'}:
        output = 'date'
    else:
        output = 'mixed'
    return output, with_none


def detect_categorical(values, typestr):

    # Categorical if: number of values is small (e.g. 1/5 of records and less than 20)
    distinct_values = len(set(values))
    if len(values) / distinct_values >= 3 and distinct_values < 20:
        return True
    else:
        return False


def p1(p):
    if p is None:
        return p
    else:
        return p + 1


def m1(p):
    if p is None:
        return p
    else:
        return p - 1


def slices_to_ranges(spec, nrows, ncols=None):
    if isinstance(spec, tuple) and len(spec) == 2:
        sl1, sl2 = spec
        return slices_to_ranges(sl1, nrows)[:2] + slices_to_ranges(sl2, ncols)[:2]
    elif isinstance(spec, slice):
        if spec.step and spec.step != 1:
            raise ValueError('Step not supported!')
        ixs = spec.indices(nrows)
        return ixs[0], ixs[1]-1, None, None
    elif isinstance(spec, int):
        if spec == -1:
            spec1 = None
        else:
            spec1 = spec + 1
        return slices_to_ranges(slice(spec, spec1), nrows, ncols)


def functioncall_str(f, args, kwargs):
    args = ['%s' % (a,) for a in args]
    args += ['%s=%s' % kv for kv in kwargs.items()]
    return '%s(%s)' % (f.__name__, ','.join(args))


def debugcall(f):
    def _wrap(*args, **kwargs):
        res = f(*args, **kwargs)
        print ('FUNCTION', functioncall_str(f, args, kwargs), ' => ', res)
        return res
    return _wrap


def first(lst):
    """Get the first element from a collection.

    This works on iterators, generators and indexed collections.

    :param lst:
    :return:
    """
    try:
        return next(lst)
    except TypeError:
        return lst[0]


def list_to_slice(lst):
    a = lst[0]
    b = lst[-1]
    assert a == min(lst)
    assert b == max(lst)
    assert b - a == len(lst) - 1
    return slice(a, b + 1)


class AbstractMethod(NotImplementedError):

    def __init__(self):
        record = inspect.stack()[1]
        try:
            classname = record[0].f_locals['self'].__class__.__name__ + '.'
        except KeyError:
            classname = ''
        funcname = record[3]
        fullname = '%s%s' % (classname, funcname)
        super(AbstractMethod, self).__init__('%s is an abstract method' % fullname)
