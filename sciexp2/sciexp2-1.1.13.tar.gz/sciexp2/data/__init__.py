#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Data manipulation abstractions.

Unless explicitly provided here, all `numpy.ndarray` methods and free functions
from `numpy` and `numpy.lib.recfunctions` should work properly with any type of
arrays (`Data` and non-`Data`).

"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import collections
import functools
import inspect
import itertools
import numpy
import numpy as np                      # required for some numpy docstrings
from numpy.lib import recfunctions
import re
import six
from six.moves import zip as _zip
import sys
import warnings
import weakref

from sciexp2.common import compat
from sciexp2.common import progress
import sciexp2.common.filter
from sciexp2.common import pp
from sciexp2.common import varref
import sciexp2.common.instance
from sciexp2.common.compat import StringIO
from sciexp2.data.io import _convert_bytes_value_maybe


"""
.. todo::

   redefine 'numpy.core.numeric.{save,savez,savetxt}' so that a message can be
   shown

.. todo::

   redefine 'numpy.core.numeric.load' so that a message can be shown

"""


######################################################################
# * Creation

def data_array(object, dims=None, *args, **kwargs):
    """Create a new array with dimension metadata.

    Parameters
    ----------
    object : array_like
        See `numpy.array`.
    dims : optional
        See argument `dims` in `Data` (default is ``object``).
    args, kwargs
        Extra arguments to `numpy.array`.

    See also
    --------
    Data, numpy.array

    """
    dtype = kwargs.pop("dtype", None)
    if dtype is None and len(args) > 0:
        try:
            dtype = numpy.dtype(args[0])
        except:
            pass
        if dtype is not None:
            args = args[1:]
    elif dtype is None and isinstance(object, numpy.ndarray):
        dtype = object.dtype
    if dtype is not None:
        kwargs["dtype"] = dtype

    shape = numpy.shape(object)
    if not isinstance(object, numpy.ndarray):
        # fixup shape if it's producing a structured array
        if isinstance(dtype, collections.Iterable):
            dtype = list(dtype)
            if dtype is not None and len(shape) > 1 and \
               shape[-1] == len(dtype):
                shape = shape[:-1]

    if dims is None and isinstance(object, Data):
        dims = object

    res = Data(shape, dims, *args, **kwargs)
    res.view(np.ndarray)[:] = object
    return res


def data_frombuffer(buffer, dims, *args, **kwargs):
    """Create an array with dimension metadata from a buffer.

    Parameters
    ----------
    buffer
        See argument `buffer` in `numpy.frombuffer`.
    dims
        See argument `dims` in `Data`.
    args, kwargs
        Arguments to `numpy.frombuffer`.

    See also
    --------
    numpy.frombuffer

    """
    arr = numpy.frombuffer(buffer, *args, **kwargs)
    return Data(shape=arr.shape, dims=dims, dtype=arr.dtype, buffer=arr)


def data_memmap(filename, dims, *args, **kwargs):
    """Create an array with dimension metadata from a buffer.

    Parameters
    ----------
    filename
        See argument `filename` in `numpy.memmap`.
    dims
        See argument `dims` in `Data`.
    args, kwargs
        Arguments to `numpy.memmap`.

    See also
    --------
    numpy.memmap

    """
    arr = numpy.memmap(filename, *args, **kwargs)
    res = Data(shape=arr.shape, dims=dims, dtype=arr.dtype, buffer=arr)
    # attributes
    res._memmap_array = arr
    res.filename = arr.filename
    res.offset = arr.offset
    res.mode = arr.mode
    # methods
    res.flush = arr.flush
    return res


######################################################################
# * Data

##################################################
# ** ufunc helpers

def _wrap_npfunc(npfunc, wrapper):
    """Wrap numpy ufuncs."""

    wrapper.func_name = npfunc.__name__
    wrapper.func_doc = npfunc.__doc__
    wrapper.__name__ = npfunc.__name__
    wrapper.__doc__ = npfunc.__doc__
    return wrapper


def _get_axis(axis, args):
    if isinstance(args, dict):
        datas = [val
                 for key, val in args.items()
                 if key != "out" and isinstance(val, Data)]
    else:
        datas = [val
                 for val in args
                 if isinstance(val, Data)]

    if len(datas) == 0:
        return None, axis
    elif len(datas) == 1:
        arg = datas[0]
        if isinstance(axis, tuple):
            new_axis = []
            for a in axis:
                if isinstance(a, six.string_types):
                    a = arg.dims[a].index
                new_axis.append(a)
            return arg, tuple(new_axis)
        elif axis is None:
            return arg, axis
        else:
            return arg, arg.dims[axis].index
    else:
        res_data = None
        res_axis = None
        for data in datas:
            _, data_axis = _get_axis(axis, [data])
            if res_axis is None:
                res_data = data
                res_axis = data_axis
            elif res_axis != data_axis:
                raise IndexError(
                    "axis translates to different dimensions on each argument")
        return res_data, res_axis


def wrap_reduce(func):
    """Wrap reductions to keep dimension metadata consistent.

    Due to numpy internals, this wrapper might raise a `ShapeError`
    exception. If so, the manual equivalent of:

    >>> f_wrap = wrap_reduce(func)  # doctest: +SKIP
    >>> d = f_wrap(data, axis=a)    # doctest: +SKIP

    is:

    >>> d = func(data, axis=a)          # doctest: +SKIP
    >>> d_dims = DataDims(data.dims)    # doctest: +SKIP
    >>> del d_dims[a]                   # doctest: +SKIP
    >>> d = Data(d, dims=d_dims)        # doctest: +SKIP

    """
    func_proto = func
    if not inspect.isfunction(func):
        func_proto = getattr(numpy, func.__name__)
    func_argspec = compat.InspectSignature(func_proto)
    assert "axis" in func_argspec
    func_axis_index = func_argspec.index("axis")
    if "out" in func_argspec:
        func_out_index = func_argspec.index("out")
    else:
        func_out_index = None

    def wrapper(*args, **kwargs):
        callargs = compat.InspectBind(func_proto, *args, **kwargs)
        keepdims = callargs.arguments["keepdims"]
        if hasattr(numpy, "_NoValue") and keepdims is numpy._NoValue:
            # numpy 1.12.0 (75ae820) started passing numpy._NoValue by default
            keepdims = False
        if len(args) <= func_axis_index:
            axis = callargs.arguments["axis"]
        else:
            axis = args[func_axis_index]
        if func_out_index is not None and len(args) <= func_out_index:
            out = callargs.arguments["out"]
        else:
            out = None

        arg, axis = _get_axis(axis, callargs.arguments)

        if len(args) <= func_axis_index:
            kwargs["axis"] = axis
        else:
            args = list(args)
            args[func_axis_index] = axis

        res = func(*args, **kwargs)

        def get_dims(dims, axis, keepdims):
            assert keepdims or axis is not None
            if axis is None:
                axis = tuple(range(len(dims)))
            if isinstance(axis, tuple):
                if keepdims:
                    new_dims = list(dims)
                    for a in axis:
                        new_dims[a] = meta.Dim(
                            new_dims[a]._expression, [None])
                    res = DataDims(new_dims)
                else:
                    res = DataDims(dims)
                    del res[list(axis)]
            else:
                if keepdims:
                    new_dims = list(dims)
                    new_dims[axis] = meta.Dim(
                        new_dims[axis]._expression, [None])
                    res = DataDims(new_dims)
                else:
                    res = DataDims(dims)
                    del res[axis]
            return res

        if isinstance(res, Data) and not isinstance(out, Data):
            if res.ndim == 0:
                return res.dtype.type(res)

            if axis is not None:
                if not _check_shape(res):
                    assert arg
                    res.dims[:] = get_dims(arg.dims, axis, keepdims)
            else:
                # had zero-dimensional result
                pass
            _ensure_shape(res)
        elif (axis is not None or keepdims) and \
             out is None and numpy.shape(res) != tuple():
            res = data_array(res, dims=get_dims(arg.dims, axis, keepdims))

        return res

    return _wrap_npfunc(func, wrapper)


def wrap_accumulate(func):
    """Wrap accumulations to keep dimension metadata consistent."""
    func_proto = func
    if not inspect.isfunction(func):
        func_proto = getattr(numpy, func.__name__)
    func_argspec = compat.InspectSignature(func_proto)
    assert "axis" in func_argspec
    func_axis_index = func_argspec.index("axis")

    def wrapper(*args, **kwargs):
        callargs = compat.InspectBind(func_proto, *args, **kwargs)
        if len(args) <= func_axis_index:
            axis = callargs.arguments["axis"]
        else:
            axis = args[func_axis_index]

        arg, axis = _get_axis(axis, callargs.arguments)

        if len(args) <= func_axis_index:
            kwargs["axis"] = axis
        else:
            args = list(args)
            args[func_axis_index] = axis

        res = func(*args, **kwargs)

        if isinstance(res, Data):
            if axis is None:
                assert arg is not None and res.size == arg.size
                res = res.view(numpy.ndarray)
            else:
                _ensure_shape(res)

        return res

    return _wrap_npfunc(func, wrapper)


##################################################
# ** misc helpers

class ShapeError (Exception):
    """Mismatching array and metadata shape."""
    def __init__(self, data_shape, dims_shape):
        self.data_shape = data_shape
        self.dims_shape = dims_shape

    def __str__(self):
        return "Data object shape '%s' and dimension metadata "\
            "'%s' are not consistent" % (self.data_shape, self.dims_shape)


def _check_shape(arr, dims=None):
    """Check if the array and the dimension metadata have the same size."""
    if dims is None:
        dims = arr.dims

    if arr.ndim != len(dims):
        return False
    for nd in range(arr.ndim):
        if arr.shape[nd] != len(dims[nd]):
            return False
    return True


def _ensure_shape(arr):
    """Ensure the array and the dimension metadata have the same size."""
    dims = arr.dims
    if not _check_shape(arr, dims):
        dims_shape = tuple([len(d) for d in dims])
        raise ShapeError(arr.shape, dims_shape)


class ReshapeError (Exception):
    """Error during `Data.reshape`."""

    def __init__(self, expression, elem1, elem2, variables):
        super(ReshapeError, self).__init__(expression,
                                           dict(elem1), dict(elem2),
                                           variables)

    def __str__(self):
        msg = "Ambiguous dimensions; unused variables: "
        msg += ", ".join(self.args[3])
        msg += "\nConflicting source elements with expression: %s\n" %\
               self.args[0]
        msg += "   %s\n" % (self.args[1])
        msg += "   %s" % (self.args[2])
        return msg


def _reshape_parse_fields_to_vars(f2v, data):
    res = []
    for f2v_re in f2v:
        match = False
        f2v_cre = re.compile(f2v_re)
        for data_field in data.dtype.names:
            if f2v_cre.match(data_field) is not None:
                match = True
                if data_field in res:
                    continue
                if data_field in data.dims[0].variables:
                    raise ValueError("Field in `fields_to_vars` already "
                                     "exists as a variable: %s" % data_field)
                res.append(data_field)
        if not match:
            raise ValueError("Value in `fields_to_vars` does not match "
                             "any field: %s" % f2v_re)
    if len(data.dtype) > 0 and set(res) == set(data.dtype.names):
        raise ValueError("Cannot move all fields into variables with "
                         "`fields_to_vars`")
    return res


def _reshape_parse_vars_to_fields(v2f, data):
    res = []
    for v2f_re in v2f:
        match = False
        v2f_cre = re.compile(v2f_re)
        for data_var in data.dims[0].variables:
            if v2f_cre.match(data_var) is not None:
                match = True
                if data_var in res:
                    continue
                if data_var in data.dtype.names:
                    raise ValueError("Variable in `vars_to_fields` already "
                                     "exists as a field: %s" % data_var)
                res.append(data_var)
        if not match:
            raise ValueError("Value in `vars_to_fields` does not match "
                             "any variable: %s" % v2f_re)
    if len(data.dtype) > 0 and set(res) == set(data.dims[0].variables):
        raise ValueError("Cannot move all variables into fields with "
                         "`vars_to_fields`")
    return res


def _reshape_compute_data(f2v, v2f, data):
    if len(f2v) != 0 and len(f2v) < len(data.dtype):
        data = recfunctions.drop_fields(data.view(numpy.ndarray), f2v)
    if len(v2f) != 0:
        new_data = [numpy.array([elem[var] for elem in data.dims[0].instances])
                    for var in v2f]
        if len(f2v) == len(data.dtype):
            data = append_fields(new_data[0], names=v2f[1:], data=new_data[1:])
        else:
            data = append_fields(data, names=v2f, data=new_data)
    return data


def _reshape_compute_dimension(f2v, v2f, data):
    if len(f2v) == 0 and len(v2f) == 0:
        return data.dims[0]
    expression = data.dims[0].expression
    if len(v2f) > 0:
        variables = [var for var in data.dims[0].variables
                     if var not in v2f]
        expression = "@%s@" % "@-@".join(variables)
    if len(f2v) > 0:
        expression += "-@%s@" % "@-@".join(f2v)

    contents = []
    with progress.progressable_simple(
            data.dims[0].instances, None,
            msg="recomputing dimension contents...") as old_dimension:
        for elem in old_dimension:
            elem_idx = data.dims[0].indexes[elem]
            elem = elem.copy()
            for field in f2v:
                value = data[elem_idx][field]
                value = _convert_bytes_value_maybe(value, data.dtype[field])
                elem[field] = value
            contents.append(elem)
    return meta.Dim(expression, contents)


def _reshape_parse_filling_values(filling_values, dtype):
    if isinstance(filling_values, dict):
        if len(dtype) == 0:
            raise ValueError("Invalid `filling_values`, array has no "
                             "fields")
        for field in filling_values:
            if field not in dtype.names:
                raise ValueError("Unknown field name %r in "
                                 "'filling_values'" % field)
    elif len(dtype) > 0 and filling_values is not None:
        filling_values = dict([(name, filling_values)
                               for name in dtype.names])
    return _reshape_filling_values(filling_values, dtype)


def _reshape_parse_ignore(ignore, dim_variables):
    ignore_rest = False
    if ignore is True:
        ignore_rest = True
        ignore = set()
    else:
        if not isinstance(ignore, list) and not isinstance(ignore, set):
            raise TypeError("Unknown `ignore` value: %s" % ignore)
        ignore = set(ignore)
        source_variables = set(dim_variables)
        if len(ignore - source_variables) > 0:
            raise ValueError("Invalid variables in `ignore`: " +
                             ", ".join(ignore - source_variables))
    return ignore, ignore_rest


def _reshape_filling_values(filling_values, dtype):
    if len(dtype) == 0:
        fdtype = numpy.dtype([("f0", dtype)])
    fdtype = numpy.dtype(dtype.descr + [("__flast__", int)])

    contents = "," * (len(fdtype) - 1)
    contents += "1"
    values = numpy.genfromtxt(StringIO(contents), delimiter=",", dtype=fdtype)

    if len(dtype) == 0:
        if filling_values is not None:
            try:
                values["f0"] = filling_values
            except:
                raise ValueError("Incompatible `filling_values` type")
        return values["f0"]
    else:
        if filling_values is not None:
            for k, v in six.iteritems(filling_values):
                try:
                    values[k] = v
                except:
                    raise ValueError("Incompatible `filling_values` type for "
                                     "field %r" % k)
        return tuple(values.tolist()[:-1])


##################################################
# ** main code

def _indexes_normalize(index, ndim, identify=False):
    """
    Examples
    --------

    >>> norm = _indexes_normalize
    >>> norm(1, 3)
    [1, slice(None, None, None), slice(None, None, None)]

    >>> norm((1, Ellipsis), 3)
    [1, slice(None, None, None), slice(None, None, None)]
    >>> norm((1, np.newaxis), 3)
    [1, None, slice(None, None, None), slice(None, None, None)]
    >>> norm((np.newaxis, 1), 3)
    [None, 1, slice(None, None, None), slice(None, None, None)]
    >>> norm((np.newaxis, 1, Ellipsis), 3)
    [None, 1, slice(None, None, None), slice(None, None, None)]

    >>> norm((Ellipsis, 1), 3)
    [slice(None, None, None), slice(None, None, None), 1]
    >>> norm((Ellipsis, 1, np.newaxis), 3)
    [slice(None, None, None), slice(None, None, None), 1, None]
    >>> norm((np.newaxis, Ellipsis, 1), 3)
    [None, slice(None, None, None), slice(None, None, None), 1]
    >>> norm((Ellipsis, np.newaxis, 1), 3)
    [slice(None, None, None), slice(None, None, None), None, 1]

    """

    # http://docs.scipy.org/doc/numpy/reference/arrays.indexing.html#basic-slicing
    #
    # "In order to remain backward compatible with a common usage in
    # Numeric, basic slicing is also initiated if the selection object is
    # any sequence (such as a list) containing slice objects, the Ellipsis
    # object, or the newaxis object, but no integer arrays or other
    # embedded sequences."
    def is_numeric_basic_slicing(indexes):
        return \
            isinstance(indexes, collections.Iterable) and \
            all(isinstance(idx, slice) or
                idx is Ellipsis or
                idx is numpy.newaxis
                for idx in indexes)

    # normalize format to a sequence of indexes
    indexes = index
    if not isinstance(indexes, tuple) and \
       not is_numeric_basic_slicing(indexes):
        indexes = [(True, indexes)]
    else:
        indexes = list((True, idx) for idx in indexes)

    # expand Ellipsis into appropriate number of empty slices
    num_newaxis = 0
    for _, i in indexes:
        if i is np.newaxis:
            num_newaxis += 1
    first_ellipsis = -1
    for idx, (_, elem) in enumerate(indexes):
        if elem is Ellipsis:
            first_ellipsis = idx
            break
    if first_ellipsis >= 0:
        indexes = [(exist, idx) if idx is not Ellipsis else (True, slice(None))
                   for exist, idx in indexes]
        span = ndim - len(indexes) + 1 + num_newaxis
        if span < 0:
            raise IndexError("too many indices")
        indexes = (indexes[:first_ellipsis] +
                   ([(False, slice(None))] * span) +
                   indexes[first_ellipsis+1:])
    else:
        span = ndim - len(indexes) + num_newaxis
        if span < 0:
            raise IndexError("too many indices")

    # add empty slices for trailing dimensions
    indexes += [(False, slice(None))] * (ndim - len(indexes) + num_newaxis)

    if not identify:
        indexes = [idx for _, idx, in indexes]
    return indexes


def _indexes_trim_suffix(indexes):
    """Trim trailing empty slices."""
    indexes = list(indexes)
    while len(indexes) > 1:
        last = indexes[-1]
        if isinstance(last, slice) and \
           last.start is None and \
           last.stop is None and \
           last.step is None:
            indexes.pop()
        else:
            break
    return indexes


class Data (numpy.ndarray, pp.Pretty):
    """Data(shape, dims, *args, **kwargs)

    N-dimensional array with dimension metadata.

    Parameters
    ----------
    shape : tuple(int)
        See `numpy.ndarray`.
    dims : `DataDims` or list, optional
        `meta.Dim` metadata.
    args, kwargs
        Extra arguments to `numpy.ndarray`.

    Notes
    -----
    The `dims` argument can be a `DataDims` instance or a sequence of valid
    arguments to its constructor. If `dims` is a list, but with less elements
    than dimensions in the array, additional empty `meta.Dim` objects will be
    added for the remaining dimensions.

    Functions with an `axis` argument can identify the target axis (`meta.Dim`)
    using the same semantics for indexing on the `dims` attribute.

    Element-wise comparison ignores the array metadata.

    See also
    --------
    data_array, numpy.ndarray, sciexp2.common.filter, reshape, meta.Dim,
    meta.Dim.sort

    Examples
    --------
    Data arrays can be accessed like regular arrays:

    >>> d = data_array([[(1, 2), (3, 4), (5, 6)],
    ...                 [(7, 8), (9, 10), (11, 12)]],
    ...                dtype = [("time", float), ("energy", float)],
    ...                dims=[("@cores@",
    ...                       ["1", "2"]),
    ...                      ("@entries@-@entry_size@",
    ...                       ["1-8", "2-8", "2-16"])])
    >>> d[0,0]["time"]
    1.0
    >>> d[0,0:2]["time"]
    data_array([1.0, 3.0], dims=[('@entries@-@entry_size@', ['1-8', '2-8'])])

    But indexing with strings will use the dimension metadata instead:

    >>> d["1","1-8"]["time"] == d[0,0]["time"]
    True
    >>> d.dims["cores"].indexes["1"] == 0 and d.dims["entries"].indexes["1-8"] == 0
    True
    >>> (d["1","1-8":"2-16"]["time"] == d[0,0:2]["time"]).all()
    True
    >>> d.dims["entries"].indexes["2-16"] == 2
    True

    Additionally, you can use filters to select specific entries, by using the
    stepping indexing argument in the slicing syntax:

    >>> d[:,::2]
    data_array([[(1.0, 2.0), (5.0, 6.0)], [(7.0, 8.0), (11.0, 12.0)]],
               dtype=[('time', '<f8'), ('energy', '<f8')],
               dims=[('@cores@', ['1', '2']),
                     ('@entries@-@entry_size@', ['1-8', '2-16'])])
    >>> d[:,::"entry_size == 8"]
    data_array([[(1.0, 2.0), (3.0, 4.0)], [(7.0, 8.0), (9.0, 10.0)]],
               dtype=[('time', '<f8'), ('energy', '<f8')],
               dims=[('@cores@', ['1', '2']),
                     ('@entries@-@entry_size@', ['1-8', '2-8'])])
    >>> d[:,::"entries == 1 && entry_size == 8"]
    data_array([[(1.0, 2.0)], [(7.0, 8.0)]],
               dtype=[('time', '<f8'), ('energy', '<f8')],
               dims=[('@cores@', ['1', '2']), ('@entries@-@entry_size@', ['1-8'])])
    >>> d[:,"entries == 1 && entry_size == 8"]
    data_array([(1.0, 2.0), (7.0, 8.0)],
               dtype=[('time', '<f8'), ('energy', '<f8')],
               dims=[('@cores@', ['1', '2'])])

    """

    _XLATOR = varref.DictXlator("@")
    _EXPANDER = sciexp2.common.instance.Expander("@")

    ##########################################################################
    # creation
    ##########################################################################

    def __new__(cls, shape, dims=None, *args, **kwargs):
        res = numpy.ndarray.__new__(cls, shape, *args, **kwargs)

        if dims is None:
            dims = []
        elif isinstance(dims, Data):
            dims = list(dims.dims)
        dims = list(dims)

        res._dims = DataDims([(None, [None] * d)
                              for d in list(res.shape)])
        res._dims._array = res
        res.dims[:len(dims)] = dims

        return res

    def __array_finalize__(self, obj):
        if obj is None:                    # explicit constructor
            pass
        elif isinstance(obj, Data):
            # just copy and hope the caller will patch it up
            self._dims = obj._dims

        else:                           # view casting into Data
            raise TypeError("cannot cast a view into a Data object")

    def __array_wrap__(self, obj, context=None):
        result = obj
        if result.ndim == 0:
            return result.item()
        if context is not None and len(context[1]) > 1:  # binary ufunc
            args = [arg
                    for arg in context[1]
                    if numpy.shape(arg) == result.shape]
            assert len(args) > 0

            def find_match():
                for arg in args:
                    # TODO: does not align metadata if multiple args match
                    if isinstance(arg, Data):
                        return arg
                return None

            match = find_match()
            if match is not None:
                if not isinstance(result, Data):
                    result = result.view(type(self))
                result._dims = match._dims.copy()
                result._dims._array = result
            else:
                if isinstance(result, Data):
                    result._dims = DataDims([(None, [None] * d)
                                             for d in list(result.shape)])
                    result._dims._array = result

        if isinstance(result, Data):
            _ensure_shape(result)
        return result

    def copy(self, order="C"):
        return data_array(self, order=order)

    copy.__doc__ = numpy.ndarray.copy.__doc__

    def _repr_pretty_(self, p, cycle):
        with self.pformat(p, cycle, name="data_array"):
            p.pretty(self.tolist())
            nd_repr = repr(self.flat[0:1].view(numpy.ndarray))
            if re.search(r"dtype=.*\)\s*$", nd_repr, re.MULTILINE) is not None:
                p.text(",")
                p.breakable()
                p.text("dtype=")
                with p.group(len("dtype="), "", ""):
                    descr = self.dtype.descr
                    if len(descr) == 1 and descr[0][0] == "":
                        p.pretty(descr[0][1])
                    else:
                        p.pretty(descr)

            p.text(",")
            p.breakable()
            p.text("dims=")
            with p.group(len("dims="), "", ""):
                dims = []
                for dim in self.dims:
                    if dim._have_expression:
                        dims += [(dim.expression, list(dim))]
                    elif list(dim._group.variables()) == [meta.Dim._DEFAULT_VAR]\
                         and len(dim._group[meta.Dim._DEFAULT_VAR]) == 0:
                        dims += [None]
                    else:
                        dims += [(None, list(dim))]
                p.pretty(dims)

    def __repr__(self):
        return pp.Pretty.__repr__(self)

    def reshape(self, *shape, **kwargs):
        """Return a copy of the array with a different shape.

        Compared to `numpy.reshape`, `Data.reshape` indicates the new shape by
        establishing which dimension metadata variables are to describe each
        dimension.


        Parameters
        ----------
        shape
            List describing each dimension of the resulting array.
        ignore : list of str, optional
            Variables that will not be used to describe dimensions. Defaults to
            an empty list, which will implicitly add a last dimension with all
            the variables not referenced in `shape`.
        filling_values : value or dict, optional
            Default values to fill-in fields previously unexisting elements
            created by reshape.
        fields_to_vars : list of str, optional
            Names of fields in the array that will be instead used as dimension
            variables (field values will be used as dimension tick values). You
            can also use regular expressions to select the matching fields.
        vars_to_fields : list of str, optional
            Names of dimension variables that will be instead used as fields in
            the result (variable values will be used as field values). You can
            also use regular expressions to select the matching variables.


        Returns
        -------
        Data
            Copy of the array with the new shape.


        Raises
        ------
        ReshapeError
            The specified `shape` is ignoring variables that have multiple
            values for a single destination element.


        Notes
        -----
        Each element in `shape` can have one of the following formats:

        * ``tuple('expression', 'filter')``
          Dimension is described by the given expression, but only taking
          elements conforming to the given filter.

        * ``'expression'``
          Shorthand to use with empty filters.

        * ``tuple(list('variable', ...), 'filter')``
          Alternative to the first format, where the list of variables is used
          to automatically build an expression.

        * ``list('variable', ...)``
          Shorthand to use with empty filters.

        Reshaping can help in working with data more efficiently, since direct
        indexing is faster than slicing filters (e.g., ``d[::"a==2"]``); but it
        can also be used to have arbitrary expressions in the dimension
        indices.

        Reshaping an array can result in more elements than the original. The
        newly-added elements are filled-in with default values, which can be
        controlled through `filling_values`. A simple value will set all fields
        to that. Using a dictionary will map field names to their default
        value.

        Examples
        --------
        Values for artificially-added elements can be controlled:

        >>> d = data_array([1, 2, 3, 4, 5],
        ...                dtype=int,
        ...                dims=[('@a@-@b@',
        ...                       ['1-1', '1-2', '1-3', '2-1', '2-2'])])
        >>> d.reshape(["a"])
        data_array([[1, 2, 3], [4, 5, -1]],
                   dims=[('@a@', ['1', '2']), ('@b@', ['1', '2', '3'])])
        >>> d.reshape(["a"], filling_values=0)
        data_array([[1, 2, 3], [4, 5, 0]],
                   dims=[('@a@', ['1', '2']), ('@b@', ['1', '2', '3'])])

        And arbitrary expressions can help later in generating axis tick names
        for plots:

        >>> d.reshape("a: @a@")
        data_array([[1, 2, 3], [4, 5, -1]],
                   dims=[('a: @a@', ['a: 1', 'a: 2']), ('@b@', ['1', '2', '3'])])

        But not all variables can be ignored. For example, ``b`` cannot be
        ignored because indices ``1-1`` and ``1-2`` have different values for
        it, unless we filter-out the offending values for ``b``:

        >>> d.reshape(["a"], ignore = True)
        Traceback (most recent call last):
            ...
        ReshapeError: Ambiguous dimensions; unused variables: b
        Conflicting source elements with expression: @a@-@b@
           {'a': 1, 'b': 1}
           {'a': 1, 'b': 2}
        >>> d.reshape((["a"], "b==2"), ignore = True)
        data_array([2, 5], dims=[('@a@', ['1', '2'])])


        See also
        --------
        numpy.reshape

        """
        if len(self.shape) != 1:
            raise ValueError("Can only reshape 1-dimensional Data objects")

        f2v = _reshape_parse_fields_to_vars(
            kwargs.pop("fields_to_vars", []),
            self)
        if "vars_to_fields" in kwargs and len(self.dtype) == 0:
            raise ValueError(
                "Cannot use 'vars_to_fields' on arrays with no fields")
        v2f = _reshape_parse_vars_to_fields(
            kwargs.pop("vars_to_fields", []),
            self)

        data = _reshape_compute_data(f2v, v2f, self)
        dimension = _reshape_compute_dimension(f2v, v2f, self)

        filling_values = _reshape_parse_filling_values(
            kwargs.pop("filling_values", None),
            data.dtype)

        ignore, ignore_rest = _reshape_parse_ignore(
            kwargs.pop("ignore", set()),
            dimension.variables)

        if len(kwargs) != 0:
            raise TypeError("Unknown arguments: " + ", ".join(kwargs.keys()))

        ##################################################
        # 0th phase
        #
        # Parse dimension descriptors.

        def parse_dimension(descriptor, prev_filter, variables, used_vars):
            """Parse and validate dimension descriptor."""
            # parsing
            res_filter = sciexp2.common.filter.Filter()
            if isinstance(descriptor, tuple):
                if len(descriptor) != 2:
                    raise ValueError("Invalid dimension descriptor: " +
                                     str(descriptor))
                res_expression = descriptor[0]
                res_filter &= descriptor[1]
            elif isinstance(descriptor, six.string_types) or\
                 isinstance(descriptor, list):
                res_expression = descriptor
            else:
                raise ValueError("Invalid dimension descriptor: " +
                                 str(descriptor))

            if isinstance(res_expression, list):
                res_expression = "@" + "@-@".join(res_expression) + "@"

            res_expression = meta.DimExpression(
                res_expression,
                varre=self.dims[0]._expression.varre,
                validate=variables)

            # validation
            res_variables = res_expression.variables
            for var in res_variables:
                if var in used_vars:
                    raise ValueError("Already used variable: %s" % var)
            # validates against the whole source, so that filters can
            # disambiguate elements when ignoring variables
            res_filter.validate(variables)

            used_vars += res_variables
            res_filter = prev_filter & res_filter
            return (res_expression, res_filter, used_vars)

        res_dim_expressions = []
        res_dim_filters = []
        res_dim_used_vars = []
        prev_filter = sciexp2.common.filter.Filter()

        # declared dimensions
        for dim_idx, descriptor in enumerate(shape):
            try:
                expression, filter_, res_dim_used_vars = parse_dimension(
                    descriptor, prev_filter, dimension.variables,
                    res_dim_used_vars)
            except (meta.DimExpressionError, ValueError,
                    sciexp2.common.filter.ParseError,
                    sciexp2.common.filter.FilterUnallowedError) as e:
                _, _, exc_traceback = sys.exc_info()
                new_e = ValueError(
                    ("While parsing descriptor for dimension %d:\n" % dim_idx) +
                    ("%s: %s" % (e.__class__.__name__, e)))
                six.reraise(new_e.__class__, new_e, exc_traceback)
            res_dim_expressions.append(expression)
            res_dim_filters.append(filter_)
            prev_filter = filter_

        # last dimension
        unused_variables = [
            variable for variable in dimension.variables
            if variable not in res_dim_used_vars and
            variable not in ignore]
        if not ignore_rest and len(unused_variables) > 0:
            try:
                expression, filter_, res_dim_used_vars = parse_dimension(
                    unused_variables, prev_filter, dimension.variables,
                    res_dim_used_vars)
            except (meta.DimExpressionError,
                    sciexp2.common.filter.ParseError,
                    sciexp2.common.filter.FilterUnallowedError) as e:
                _, _, exc_traceback = sys.exc_info()
                new_e = ValueError(
                    "While parsing descriptor for last dimension:\n"
                    "%s: %s" % (e.__class__.__name__, e))
                six.reraise(new_e.__class__, new_e, exc_traceback)
            res_dim_expressions.append(expression)
            res_dim_filters.append(filter_)

        ##################################################
        # 1st phase
        #
        # Build Dim objects for the resulting structure, while caching in
        # `res_maps` the mapping from the position of each element in `data` to
        # the position in the resulting array.

        res_dims = []         # list of Dim objects for `res`
        res_maps = []         # per-Dim maps from `data` to `res` indices

        for dim_idx, (expression, filter_) in enumerate(
                _zip(res_dim_expressions, res_dim_filters)):
            # NOTE: use internal attribute for speed
            self_dim = dimension._group

            with progress.progressable_simple(
                    self_dim, None,
                    msg="calculating dimension %d..." % dim_idx) as self_dim_progr:
                expansions = self._EXPANDER.expand(expression.expression,
                                                   self_dim_progr,
                                                   filter_=filter_,
                                                   recursive=False,
                                                   grouped=False)
            dim_map = {}

            # iterable with length
            class DimBuild (object):

                def __len__(self):
                    return len(expansions)

                def __iter__(self):
                    for dim_idx, expansion in enumerate(
                            six.itervalues(expansions)):
                        with progress.progressable_simple(
                                expansion.instances, None,
                                msg="building dimension %d..." % dim_idx) as instances:
                            instances = iter(instances)
                            try:
                                first = next(instances)
                            except StopIteration:
                                return
                            first_idx = dimension.indexes[first]
                            dim_map[first_idx] = dim_idx
                            for instance in instances:
                                instance_idx = dimension.indexes[instance]
                                dim_map[instance_idx] = dim_idx
                            yield first

            dim = meta.Dim(expression, DimBuild())

            res_dims.append(dim)
            res_maps.append(dim_map)

        ##################################################
        # 2nd phase
        #
        # Migrate data from `data` to the resulting array, using the
        # pre-computed index maps in `res_maps`.

        res_shape = tuple(len(d) for d in res_dims)

        # short-cut when shape does not change
        if list(res_shape) == list(data.shape):
            return data_array(data, dims=res_dims)

        res = Data(res_shape,
                   dims=res_dims,
                   dtype=data.dtype)

        with progress.get(res.size + 2, msg="reshaping contents...") as progr:
            progr()
            # set all default values at once for items artificially added to
            # maintain shape homogeneity
            res[:] = filling_values
            progr()
            res._fill_reshape(data, res_maps, progr)

        _ensure_shape(res)

        return res

    def _fill_reshape(self, source, self_maps, progr):
        # not space-efficient, but really fast and (hopefully) small enough
        res_set = numpy.ndarray(self.shape, dtype=int)
        res_set[:] = -1

        for source_pos in range(source.size):
            progr()
            try:
                self_pos = tuple([self_map[source_pos]
                                  for self_map in self_maps])
            except KeyError:
                # source position ignored by dimension filter
                continue
            if res_set[self_pos] >= 0:
                source1 = source.dims[0].instances[res_set[self_pos]]
                source2 = source.dims[0].instances[source_pos]
                unused = dict(source1)
                for k, v in source2:
                    if k in unused and unused[k] == v:
                        del unused[k]
                raise ReshapeError(source.dims[0].expression,
                                   source1, source2, list(unused.keys()))
            res_set[self_pos] = source_pos
            source_value = numpy.ndarray.__getitem__(
                source.view(np.ndarray), source_pos)
            numpy.ndarray.__setitem__(
                self.view(np.ndarray), self_pos, source_value)

    def _sort(self, dim, old_indexes):
        idx = self.indexer.dims[dim.index]
        self[idx[:]] = self[idx[old_indexes]]

    def __reduce__(self):
        count = sum([len(dim) for dim in self.dims])

        start = progress.get_pickle(count)
        stop = start.get_stop()

        object_state = list(numpy.ndarray.__reduce__(self))
        subclass_state = self._dims
        object_state[2] = (start, object_state[2], subclass_state, stop)
        return tuple(object_state)

    def __setstate__(self, state):
        _, nd_state, own_state, _ = state
        numpy.ndarray.__setstate__(self, nd_state)
        self._dims = own_state
        self._dims._array = self

    ##########################################################################
    # Dimension metadata accessors / manipulators
    ##########################################################################

    @property
    def dims(self):
        """`DataDims` with the dimension metadata of this array."""
        return self._dims

    @property
    def indexer(self):
        """`DataIndexer` for this array."""
        return DataIndexer(self)

    @property
    def idata(self):
        """`DataIData` for this array."""
        return DataIData(self)

    ##########################################################################
    # Item accessors / manipulators
    ##########################################################################

    def _get_indexes(self, index, need_dims):
        if isinstance(index, DataIndexer):
            index = index._get_indexes()
        indexes = _indexes_normalize(index, self.ndim)

        def calculate_fallback():
            state["copy"] = True
            state["advanced"] += 1
            if state["advanced"] > 1:
                # do not try to calculate metadata
                state["need_dims"] = False
                state["new_dims"] = None

        def reraise(exception):
            _, _, exc_traceback = sys.exc_info()
            new_e = IndexError(
                "error indexing dimension %d"
                "\n  [was] "
                "%s: %s" % (cur_dim,
                            e.__class__.__name__, str(e)))
            six.reraise(new_e.__class__, new_e, exc_traceback)

        state = dict(need_dims=need_dims,
                     copy=False,
                     advanced=0,
                     new_dims=[])
        ignore_indexes_from = None
        cur_dim = 0
        new_indexes = [([], [])]

        for i, index in enumerate(indexes):
            if i == ignore_indexes_from:
                break
            if index is numpy.newaxis:
                state["new_dims"].append(meta.Dim(None, [None]))
                new_indexes[-1][0].append(slice(None))
                new_indexes[-1][1].append(index)
            elif isinstance(index, np.ndarray) and index.dtype is np.dtype(bool):
                if self.shape == index.shape:
                    # ignore suffix slices added by normalization
                    wo_suffix = _indexes_trim_suffix(indexes)
                    ignore_indexes_from = len(wo_suffix)
                if len(self.shape) > 1:
                    # TODO: cannot build any meaningful metadata (unless
                    # flattened)
                    calculate_fallback()
                    calculate_fallback()
                elif state["need_dims"]:
                    new_dim, _ = self.dims[cur_dim]._view(index)
                    if state["copy"]:
                        new_dim = new_dim.copy()
                    state["new_dims"].append(new_dim)
                new_indexes[-1][0].append(slice(None))
                new_indexes[-1][1].append(index)
            else:
                if isinstance(index, sciexp2.common.filter.PFilter):
                    index_shape = tuple()
                else:
                    index_shape = numpy.shape(index)

                append_dims = False

                if len(index_shape) > 0:  # advanced indexing (numpy)
                    append_dims = True
                    calculate_fallback()
                    if len(index_shape) > 1:
                        calculate_fallback()

                if state["need_dims"]:
                    # NOTE: get both in a single call
                    try:
                        new_dim, new_index = self.dims[cur_dim]._view(index)
                    except Exception as e:
                        reraise(e)
                else:
                    new_dim = None
                    try:
                        new_index = self.dims[cur_dim]._get_indexes(index)
                    except Exception as e:
                        reraise(e)

                is_filter = False
                new_index_shape = numpy.shape(new_index)

                if len(index_shape) == 0:
                    if len(new_index_shape) > 0:
                        # complex filter: must be applied on a separate access
                        # to avoid advanced indexing
                        append_dims = True
                        is_filter = True
                        if len(new_indexes[-1][1]) > 0:
                            new_indexes.append(([], []))
                    elif isinstance(index, slice):
                        append_dims = True

                if len(new_index_shape) > 0:
                    new_index = list(new_index)

                if state["need_dims"] and append_dims:
                    state["new_dims"].append(new_dim)
                if append_dims:
                    new_indexes[-1][0].append(slice(None))
                new_indexes[-1][1].append(new_index)
                if is_filter:
                    new_indexes.append(([], []))
                cur_dim += 1

        if new_indexes[-1][1] == []:
            new_indexes = new_indexes[:-1]

        return state["new_dims"], new_indexes

    def __getitem__(self, index):
        # try as a field name
        field_maybe = isinstance(index, six.string_types) and \
                      len(self.dtype) > 0
        if field_maybe and index in self.dtype.names:
            return numpy.ndarray.__getitem__(self, index)

        # try as an index
        try:
            dims, indexes = self._get_indexes(index, True)
        except IndexError as e:
            if field_maybe:
                # mimic numpy's field indexing error (ValueError)
                _, _, exc_traceback = sys.exc_info()
                new_e = ValueError(
                    ("field or tick named %s not found\n" % index) +
                    ("%s: %s" % (e.__class__.__name__, e)))
                six.reraise(new_e.__class__, new_e, exc_traceback)
            else:
                raise

        # nested indexing to support filters
        source = self
        prefix = []
        for idx_prefix, idx in indexes:
            idx = prefix + idx
            # trim tail empty slices
            while len(idx) > 0 and \
                  isinstance(idx[-1], slice) and \
                  idx[-1] == slice(None):
                idx = idx[:-1]
            if len(idx) > 0:
                if len(idx) == 1:
                    idx = idx[0]
                else:
                    idx = tuple(idx)
                res = source = numpy.ndarray.__getitem__(source, idx)
            else:
                res = source = numpy.ndarray.__getitem__(source, slice(None))
            prefix += idx_prefix

        if dims is None:
            res._dims = DataDims([meta.Dim(None, None)] * len(res.shape))
            res._dims._array = res

        elif len(res.shape) > 0:       # could be a record
            # avoid Dim copies
            # (no need to check variable consistency)
            res._dims = DataDims(dims)
            res._dims._array = res

            self_base = self.base if self.base is not None else self
            res_base = res.base if res.base is not None else res
            if res_base is not self_base:
                # copy dims: advanced indexing always returns a copy
                for idx, d in enumerate(res.dims):
                    if d.base is not None:
                        res._dims._dims[idx] = d.copy()
                        res._dims._dims[idx]._dims = res.dims
                    assert res.dims[idx].base is None

            for d in res.dims:
                d._dims = res._dims
            _ensure_shape(res)

        return res

    def __getslice__(self, start, stop):
        if start is 0:
            start = None
        if stop == sys.maxint:
            return self[start::]
        else:
            return self[start:stop:]

    def __setitem__(self, index, value):
        # set field
        if isinstance(index, six.string_types) and \
           len(self.dtype) > 0 and \
           index in self.dtype.names:
            numpy.ndarray.__setitem__(self.view(np.ndarray), index, value)
            return

        _, indexes = self._get_indexes(index, False)
        indexes = [i for _, idx in indexes for i in idx]
        numpy.ndarray.__setitem__(self.view(np.ndarray), tuple(indexes), value)

    def __setslice__(self, start, stop, value):
        if start is 0:
            start = None
        if stop == sys.maxint:
            self[start::] = value
        else:
            self[start:stop:] = value

    ##########################################################################
    # Miscellaneous methods
    ##########################################################################

    def _imag(self):
        res = self.view(numpy.ndarray).imag
        return data_array(res, dims=self)

    imag = property(_imag, doc=numpy.ndarray.imag.__doc__)

    def _real(self):
        res = self.view(numpy.ndarray).real
        return data_array(res, dims=self)

    real = property(_real, doc=numpy.ndarray.imag.__doc__)

    def ravel(self, order="C"):
        if order == "K":
            raise ValueError("Ravel with order 'K' not supported")

        res = self.view(numpy.ndarray).ravel(order)
        return data_array(res, dims=_flat_dimensions(self, order))

    ravel.__doc__ = numpy.ndarray.ravel.__doc__

    def transpose(self, *axes):
        res = numpy.ndarray.transpose(self, *axes)
        dims = self.dims
        if len(axes) == 0 or (len(axes) == 1 and axes[0] is None):
            dims = dims[::-1]
        else:
            if len(axes) == 1 and isinstance(axes[0], collections.Iterable):
                axes = axes[0]
            new_dims = list(dims)
            for i, ax in enumerate(axes):
                new_dims[i] = dims[ax]
            dims = new_dims
        return data_array(res, dims=dims)

    transpose.__doc__ = numpy.ndarray.transpose.__doc__

    def _T(self):
        if self.ndim < 2:
            return self
        return self.transpose()

    T = property(_T, doc=numpy.ndarray.T.__doc__)

    def flatten(self, order='C'):
        res = numpy.ndarray.flatten(self, order)
        return data_array(res, dims=_flat_dimensions(self, order))

    flatten.__doc__ = numpy.ndarray.flatten.__doc__

    def sort(self, axis=-1, kind='quicksort', order=None):
        axis = _get_axis(axis, [self])[1]
        view = self.view(numpy.ndarray)

        if len(self.shape) == 0:
            # let it fail through numpy.ndarray.sort
            numpy.ndarray.sort(view, axis=axis, kind=kind, order=order)
            assert False
        elif len(self.shape) == 1:
            indexes = numpy.argsort(view, axis=axis, kind=kind, order=order)
            self[:] = self[indexes]
            self.dims[0][:] = self.dims[0][indexes]
        else:
            raise ValueError("cannot sort multi-dimensional Data")

    # Data needs its own examples
    sort.__doc__ = re.sub(r">>> (.*)", r">>> \1 #doctest: +SKIP",
                          numpy.ndarray.sort.__doc__)

    ##########################################################################
    # Patched methods
    ##########################################################################

    mean = wrap_reduce(numpy.ndarray.mean)
    var = wrap_reduce(numpy.ndarray.var)
    std = wrap_reduce(numpy.ndarray.std)

    min = wrap_reduce(numpy.ndarray.min)
    max = wrap_reduce(numpy.ndarray.max)

    sum = wrap_reduce(numpy.ndarray.sum)
    prod = wrap_reduce(numpy.ndarray.prod)

    all = wrap_reduce(numpy.ndarray.all)
    any = wrap_reduce(numpy.ndarray.any)

    argmax = wrap_reduce(numpy.ndarray.argmax)
    argmin = wrap_reduce(numpy.ndarray.argmin)

    cumsum = wrap_accumulate(numpy.ndarray.cumsum)
    cumprod = wrap_accumulate(numpy.ndarray.cumprod)

    def __eq__(self, other):
        # TODO: handle metadata (check "Notes")
        return numpy.ndarray.__eq__(self.view(numpy.ndarray), other)

    def choose(self, choices, out=None, mode='raise'):
        res = numpy.ndarray.choose(self, choices, out=out, mode=mode)
        if out is not None:
            return res
        found = False
        for c in choices:
            if isinstance(c, Data):
                if c.dtype == res.dtype:
                    found = True
                break
        if not found:
            res = numpy.array(res)
        return res
    choose.func_doc = numpy.ndarray.choose.__doc__


def _patched_wrapper(name):
    """Wrap unhandled `numpy.ndarray` methods to return arrays without metadata.

    """
    func = getattr(numpy.ndarray, name)
    @functools.wraps(func, assigned=["__name__"])
    def wrapper(self, *args, **kwargs):
        ndself = self.view(numpy.ndarray)
        res = func(ndself, *args, **kwargs)
        return data_array(res)
    wrapper.__doc__ = "Wrapper for `numpy.ndarray.%s`." % name
    return wrapper


def _patch_methods():
    for name, obj in inspect.getmembers(Data):
        if inspect.getmodule(obj) == inspect.getmodule(Data):
            continue
        if name[0] == "_":
            continue
        if not callable(obj):
            continue
        # whitelist
        if name in [
                "byteswap", "dump", "fill", "getfield", "item", "itemset",
                "newbyteorder", "pformat", "put", "setfield", "setflags",
                "tolist", "tostring", "view"
        ]:
            continue
        setattr(Data, name, _patched_wrapper(name))

_patch_methods()


def _flat_dimensions(data, order):
    dims = data.dims

    expression = "-".join([dim.expression for dim in dims])

    if order == "A":
        order = "F" if numpy.isfortran(data) else "C"
    reverse = (order == "F")
    if reverse:
        dims = dims[::-1]

    def recurse(current, dims, result, reverse):
        if len(dims) == 0:
            result.append(current)
        else:
            if reverse:
                rest = dims[:-1]
                dim = dims[-1]
            else:
                rest = dims[1:]
                dim = dims[0]
            rest = dims[1:]
            dim = dims[0]
            for elem in dim.instances:
                if current is None:
                    cur = None
                else:
                    cur = sciexp2.common.instance.Instance(current)
                    if elem is None:
                        cur = None
                    else:
                        cur.update(elem)
                recurse(cur, rest, contents, reverse)

    contents = []
    recurse({}, dims, contents, reverse)

    return [meta.Dim(expression, contents)]


######################################################################
# * DataDims

class DataDims (pp.Pretty):
    """A collection of data dimensions that can be operated like a list.

    Parameters
    ----------
    values : DataDims, Data or list(meta.Dim)

    Notes
    -----
    The `values` argument can be a `DataDims` or `Data` object, in which case
    their metadata will be used.

    If `values` is a sequence, each element can be:

    * a `meta.Dim` object
    * a tuple with arguments for the `meta.Dim` constructor
    * a string with the first argument for the `meta.Dim` constructor

    Examples
    --------
    Dimensions are represented as a list:

    >>> dims = DataDims([('@a@-@b@', ['0-0']), ('@c@', ['0'])])
    >>> dims
    [Dim('@a@-@b@', ['0-0']), Dim('@c@', ['0'])]

    Dimensions can be retrieved using numeric indexes:

    >>> dims[0]
    Dim('@a@-@b@', ['0-0'])
    >>> dims[1]
    Dim('@c@', ['0'])

    Strings can also be used, referring to a variable name in a dimension, or
    the expression of such dimension:

    >>> dims['a']
    Dim('@a@-@b@', ['0-0'])
    >>> dims['b']
    Dim('@a@-@b@', ['0-0'])
    >>> dims['@a@-@b@']
    Dim('@a@-@b@', ['0-0'])
    >>> dims['c']
    Dim('@c@', ['0'])
    >>> dims['@c@']
    Dim('@c@', ['0'])

    Multiple dimensions can also be selected:

    >>> dims['b':]
    [Dim('@a@-@b@', ['0-0']), Dim('@c@', ['0'])]
    >>> dims['c', 'a']
    [Dim('@c@', ['0']), Dim('@a@-@b@', ['0-0'])]

    And dimensions can also be re-assigned:

    >>> dims['c'] = meta.Dim('@z@', ['foo'])
    >>> dims
    [Dim('@a@-@b@', ['0-0']), Dim('@z@', ['foo'])]

    As well as deleted:

    >>> del dims['z']
    >>> dims
    [Dim('@a@-@b@', ['0-0'])]

    """

    def __init__(self, values):
        self.__array = None
        if isinstance(values, DataDims):
            self._dims = np.ndarray(len(values), dtype=object)
            self._dims[:] = values.copy()
        elif isinstance(values, Data):
            self._dims = np.array(list(values.dims.copy()), dtype=object)
        else:
            self._dims = np.array([None] * len(values), dtype=object)
            self._dims[:] = [[]] * len(values)
            self[:] = values

    @property
    def _array(self):
        if self.__array is None:
            return None
        else:
            return self.__array()

    @_array.setter
    def _array(self, array):
        self.__array = weakref.ref(array)

    def __eq__(self, other):
        return isinstance(other, DataDims) and \
            len(self) == len(other) and \
            all(d1._expression == d2._expression and \
                len(d1) == len(d2) and \
                list(d1.ticks) == list(d2.ticks)
                for d1, d2 in zip(self, other))

    def _repr_pretty_(self, p, cycle):
        return p.pretty(list(self._dims))

    def __repr__(self):
        return pp.Pretty.__repr__(self)

    def copy(self):
        """Return a list with a deep copy of the dimension metadata."""
        return DataDims([d.copy() for d in self._dims])

    def __iter__(self):
        return iter(self._dims)

    def __len__(self):
        return len(self._dims)

    def _get_index_one(self, index, is_slice=False):
        if index is None and is_slice:
            return None
        elif isinstance(index, int):
            return index
        elif isinstance(index, tuple):
            return [self._get_index_one(idx)
                    for idx in index]
        elif isinstance(index, six.string_types):
            for idx, dim in enumerate(self._dims):
                if not dim._have_expression:
                    continue
                if index in dim.variables:
                    return idx
                if index == dim.expression:
                    return idx
            raise ValueError(
                "no dimension with given expression or variable name: %r" %
                index)
        else:
            raise TypeError("invalid dimension index: %r" % index)

    def _get_index(self, index):
        if isinstance(index, slice):
            return slice(
                self._get_index_one(index.start, is_slice=True),
                self._get_index_one(index.stop, is_slice=True),
                index.step)
        elif isinstance(index, list):
            return [self._get_index_one(idx)
                    for idx in index]
        else:
            return self._get_index_one(index)

    def __getitem__(self, index):
        idx = self._get_index(index)
        res = self._dims[idx]
        if isinstance(res, np.ndarray):
            return list(res)
        else:
            return res

    def __setitem__(self, index, value):
        idx = self._get_index(index)
        if isinstance(value, Data):
            value = value.dims
        if isinstance(value, DataDims):
            value = list(value)

        def as_dim(value, old_size):
            if value is None:
                res = meta.Dim(None, [None] * old_size)
            elif isinstance(value, meta.Dim):
                def array_base(array):
                    if array is not None and array.base is not None:
                        return array.base
                    else:
                        return array
                # use a view for all Dim objects of a view to this array
                if value.array is self._array:
                    res = value
                elif array_base(value.array) is array_base(self._array):
                    res = value._view(slice(None))[0]
                else:
                    res = value.copy()
            elif isinstance(value, six.string_types):
                res = meta.Dim(value, [None] * old_size)
            elif isinstance(value, collections.Sized) and len(value) == 2:
                contents = value[1]
                if contents is None:
                    contents = [None] * old_size
                res = meta.Dim(value[0], contents)
            else:
                raise TypeError("cannot build a dimension from: %s" %
                                repr(value))
            res._dims = self
            return res

        # apply changes

        new_dims = np.ndarray((len(self._dims),), dtype=object)
        new_dims[:] = self._dims

        if self._array is None:
            tmp_dims = new_dims[idx]
            if isinstance(tmp_dims, meta.Dim):
                old_sizes = [len(tmp_dims)]
            else:
                old_sizes = [len(o) for o in tmp_dims]
        else:
            old_sizes = np.array(self._array.shape)[idx]

        if isinstance(idx, int):
            idx = slice(idx, idx+1)
            value = [as_dim(value, old_sizes)]
        elif isinstance(idx, list) or isinstance(idx, slice):
            try:
                value_len = len(value)
            except TypeError:
                value_len = None
            if value_len != len(old_sizes):
                raise ValueError(
                    "invalid number of dimension metadata objects")
            value = [as_dim(v, o) for v, o in zip(value, old_sizes)]
        else:
            raise NotImplementedError(idx)

        # check we're not replacing views
        old_values = list(new_dims[idx])
        for dim in old_values:
            if dim == []:
                continue
            if dim.base is not None:
                raise ValueError("cannot replace a view")

        if isinstance(idx, list):
            # XXX: assigning to a numpy.ndarray results in None's
            for i, v in zip(idx, value):
                new_dims[i] = v
        else:
            new_dims[idx] = value

        # verify metadata consistency
        if self._array is not None:
            if len(new_dims) != self._array.ndim:
                raise ValueError(
                    "invalid number of dimension metadata objects")
        for i, d in enumerate(new_dims):
            if self._array is not None and \
               not (d == []) and\
               len(d) != self._array.shape[i]:
                raise ValueError("metadata for dimension %d with length %d "
                                 "does not match array dimension length %d" %
                                 (i, len(d), self._array.shape[i]))
            try:
                variables = d.variables
            except (meta.DimExpressionError, AttributeError):
                continue
            for var in variables:
                for pi, pd in enumerate(new_dims[:i]):
                    try:
                        pd_variables = pd.variables
                    except meta.DimExpressionError:
                        continue
                    if var in pd_variables:
                        msg = "expression variable %r " % var
                        msg += "in dimension %d " % i
                        msg += "already present in dimension %d" % pi
                        raise ValueError(msg)

        # update views
        for old_dim, new_dim in zip(old_values, value):
            if not isinstance(old_dim, meta.Dim):
                for idx, d in enumerate(self._dims):
                    if d == old_dim:
                        break
                self._dims[idx] = new_dim
            elif old_dim is not new_dim:
                old_dim._assign(new_dim)

    def __getslice__(self, start, stop):
        if start is 0:
            start = None
        if stop == sys.maxint:
            return self[start::]
        else:
            return self[start:stop:]

    def __setslice__(self, start, stop, value):
        if start is 0:
            start = None
        if stop == sys.maxint:
            self[start::] = value
        else:
            self[start:stop:] = value

    def __delitem__(self, index):
        if self._array is not None:
            raise TypeError(
                "cannot delete a dimension from an existing Data array")
        idx = self._get_index(index)
        if not isinstance(idx, collections.Iterable):
            idx = [idx]
        new_dims = [dim
                    for i, dim in enumerate(self._dims)
                    if i not in idx]
        self._dims = np.array([None] * len(new_dims), dtype=object)
        self._dims[:] = new_dims

    def __getstate__(self):
        return {"_dims": self._dims}

    def __setstate__(self, odict):
        self.__dict__.update(odict)
        self.__array = None
        for d in self._dims:
            d._dims = self


######################################################################
# * DataIndexer

class DataIndexer(pp.Pretty):
    """Object to build an array indexing tuple across dimensions.

    This comes in handy when indexing an array without caring about the precise
    position of every dimension, and can be used to index `Data` objects.

    The `dims` attribute returns a "dimension selector", which can be indexed
    to select dimensions. Indexing the result will generate a new `DataIndexer`
    referencing the selected dimensions.


    Examples
    --------
    >>> d = data_array(numpy.arange(27).reshape((3, 3, 3)),
    ...                dims=[("@%s@" % d, ["%s%d" % (d, i) for i in range(3)])
    ...                      for d in ["a", "b", "c"]])

    Regular `Data` indexing would be:

    >>> d["a0", :, "c=='c1'":]
    data_array([[1, 2], [4, 5], [7, 8]],
               dims=[('@b@', ['b0', 'b1', 'b2']), ('@c@', ['c1', 'c2'])])

    Using `DataIndexer` allows ignoring dimension positions (useful to
    programmatically build indexing objects):

    >>> i = d.indexer
    >>> i = i.dims["a"]["a0"]
    >>> i = i.dims["c"]["c == 'c1'":]
    >>> i
    ('a0', slice(None, None, None), slice("c == 'c1'", None, None))
    >>> d[i]
    data_array([[1, 2], [4, 5], [7, 8]],
               dims=[('@b@', ['b0', 'b1', 'b2']), ('@c@', ['c1', 'c2'])])

    Multiple dimensions can also be used, resulting in the expected results:

    >>> i.dims["b"][0, np.newaxis]
    ('a0', 0, None, slice("c == 'c1'", None, None))
    >>> i.dims["c", "a"][-1, 1]
    (1, slice(None, None, None), -1)
    >>> i.dims["c", "c"][-1, 1]
    ('a0', slice(None, None, None), 1)

    You can also obtain indexes compatible with regular numpy arrays:


    >>> d.indexer.dims["a", "b", "c"]["a0", 0, np.newaxis, "c == 'c1'":].as_tuple()
    (0, 0, None, slice(1, None, None))


    Notes
    -----
    Instances of this class should be obtained through `Data.indexer`.


    See also
    --------
    Data.indexer
    Data.idata

    """

    def __init__(self, array=None, dims=None, indexes=None):
        assert ((array is not None and dims is None and indexes is None) or
                (array is None and dims is not None and indexes is not None))
        if dims is None:
            # NOTE: need the complete dimension contents for 'as_tuple'
            self._dims = array.dims
        else:
            self._dims = dims
        if indexes is None:
            self._indexes = [slice(None) for index in range(array.ndim)]
        else:
            self._indexes = list(indexes)

    def _get_indexes(self, trim=True):
        if trim:
            indexes = _indexes_trim_suffix(self._indexes)
        else:
            indexes = self._indexes
        if len(indexes) == 1:
            return indexes[0]
        else:
            return tuple(indexes)

    def as_tuple(self, trim=True):
        """Return a tuple with regular numpy indexes.

        Parameters
        ----------
        trim : bool, optional
            Omit indexing information for trailing dimensions not referenced on
            the indexer object (default: `True`).

        """
        idxs = self._get_indexes(trim=trim)
        if not isinstance(idxs, tuple):
            idxs = tuple([idxs])
        assert len(idxs) <= len(self._dims)
        res = []
        for dim, idx in zip(self._dims, idxs):
            if idx is np.newaxis:
                res.append(idx)
            else:
                res.append(dim._get_indexes(idx))
        if len(res) == 1:
            return res[0]
        else:
            return tuple(res)

    def __getitem__(self, index):
        return self.dims[:][index]

    @property
    def dims(self):
        """Proxy to indexing the selected dimensions (see `DataDims`)."""
        return _DataIndexer_Dims(self)

    def _repr_pretty_(self, p, cycle):
        return p.pretty(self._get_indexes(trim=False))

    def __repr__(self):
        return pp.Pretty.__repr__(self)


class _DataIndexer_Dims(object):
    def __init__(self, indexer):
        self._indexer = indexer

    def __getitem__(self, index):
        dims = self._indexer._dims[index]
        if isinstance(dims, meta.Dim):
            dims = [dims.index]
        else:
            dims = [dim.index for dim in dims]
        return _DataIndexer_DimsIndexer(self._indexer, dims)


class _DataIndexer_DimsIndexer(object):
    def __init__(self, indexer, dims):
        self._indexer = indexer
        self._dims = dims

    def __getitem__(self, index):
        indexes = _indexes_normalize(index, len(self._dims))

        i_dims = list(self._indexer._dims.copy())
        i_indexes = list(self._indexer._indexes)

        # set indexing info
        pos = 0
        for idx in indexes:
            if idx is np.newaxis:
                continue
            i_indexes[self._dims[pos]] = idx
            pos += 1

        # extend with newaxis
        pos -= 1
        for idx in reversed(indexes):
            if idx is not np.newaxis:
                pos -= 1
            else:
                if pos == -1:
                    dims_pos = self._dims[pos+1]
                else:
                    dims_pos = self._dims[pos] + 1
                i_dims = (i_dims[:dims_pos] +
                          [meta.Dim()] +
                          i_dims[dims_pos:])
                i_indexes = (i_indexes[:dims_pos] +
                             [np.newaxis] +
                             i_indexes[dims_pos:])

        return DataIndexer(dims=DataDims(i_dims),
                           indexes=i_indexes)


######################################################################
# * DataIndexerProxy

class DataIData(object):
    """Object to index specific array dimensions without knowing their position.

    This comes in handy as a shorthand for `DataIndexer` when the indexer
    object does not need to be reused.


    Examples
    --------
    >>> d = data_array(numpy.arange(27).reshape((3, 3, 3)),
    ...                dims=[("@%s@" % d, ["%s%d" % (d, i) for i in range(3)])
    ...                      for d in ["a", "b", "c"]])

    Shorthand of the equivalent first example in `DataIndexer`:

    >>> d.idata["a", "c"]["a0", "c == 'c1'":]
    data_array([[1, 2], [4, 5], [7, 8]],
               dims=[('@b@', ['b0', 'b1', 'b2']), ('@c@', ['c1', 'c2'])])

    You can also chain it multiple times:

    >>> d.idata["a"]["a0"].idata["c"]["c == 'c1'":]
    data_array([[1, 2], [4, 5], [7, 8]],
               dims=[('@b@', ['b0', 'b1', 'b2']), ('@c@', ['c1', 'c2'])])


    Notes
    -----
    Instances of this class should be obtained through `Data.idata`.

    Chaining this functionality multiple times (second example) creates a
    temporary result array on each step. This must be kept in mind when using
    it to assign new values, since "advanced indexing" (see NumPy documentation
    [#np.idx]_) creates copies of the data instead of a view (i.e., the
    assigned values will not reach the original array).

    .. [#np.idx] http://docs.scipy.org/doc/numpy/reference/arrays.indexing.html


    See also
    --------
    Data.idata

    """

    def __init__(self, array, indexes=None):
        self._array = array

    def __getitem__(self, index):
        indexer = self._array.indexer.dims[index]
        return _DataIData_DataIndexer(self._array, indexer)


class _DataIData_DataIndexer(object):

    def __init__(self, array, indexer):
        self._array = array
        self._indexer = indexer

    def __getitem__(self, index):
        indexer = self._indexer[index]
        return self._array[indexer]

    def __setitem__(self, index, value):
        indexer = self._indexer[index]
        self._array[indexer] = value


######################################################################
# * Public manifest

from ._funcs import *


__all__ = [
    "data_array", "data_frombuffer", "data_memmap",
    "Data", "DataDims", "DataIndexer", "DataIData",
    "wrap_reduce", "wrap_accumulate",
]

__all__ += _funcs.__all__

from sciexp2.data import meta
