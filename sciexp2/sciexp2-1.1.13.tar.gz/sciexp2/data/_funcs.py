#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Data manipulation abstractions."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import collections
import functools
import numpy
import numpy as np                      # required for some numpy docstrings
from numpy.lib import recfunctions

from sciexp2.common import compat
from sciexp2.data import Data, data_array, _get_axis
from sciexp2.data import meta


def _wraps(name):
    def wrapper(func):
        doc = func.__doc__
        func.__doc__ = "`Data`-aware wrapper for `%s`" % (name)
        if doc is not None:
            func.__doc__ += "\n" + doc
        return func
    return wrapper

##################################################
# * Concatenate / append

_numpy_concatenate = numpy.concatenate


def _concatenate(arrays, axis):
    # calculate new np.array
    _, axis = _get_axis(axis, list(arrays))
    arr_res = _numpy_concatenate(arrays, axis=axis)
    assert isinstance(axis, int), "numpy.concatenate should only accept int axis"

    if not any(isinstance(array, Data) for array in arrays):
        return arr_res

    if axis is None:
        # flattened by numpy
        return data_array(arr_res, dtype=arr_res.dtype)

    # calculate new dimensions
    res_dims = []
    for didx in range(arrays[0].ndim):
        res_dim = None
        res_expr = None
        for array in arrays:
            if not isinstance(array, Data):
                continue
            a_dim = array.dims[didx]
            try:
                a_expr = a_dim.expression
            except meta.DimExpressionError:
                a_expr = None
            if res_expr is not None and a_expr is not None and res_expr != a_expr:
                raise ValueError(
                    "incompatible dimension expressions in dimension %d" % didx)
            if (res_dim is not None and a_dim is not None and
                list(res_dim) != list(a_dim) and didx != axis):
                raise ValueError(
                    "incompatible dimension contents in dimension %d" % didx)
            if res_dim is None:
                res_dim = a_dim
            if res_expr is None and a_expr is not None:
                res_dim = a_dim
                res_expr = a_expr

        res_dim = res_dim.copy()

        if didx == axis:
            res_dim_contents = []
            for array in arrays:
                if isinstance(array, Data):
                    res_dim_contents.extend(list(array.dims[didx]))
                else:
                    res_dim_contents.extend([None] * array.shape[didx])
                res_dim = meta.Dim(res_expr, res_dim_contents)

        res_dims.append(res_dim)

    return data_array(arr_res, dims=res_dims, dtype=arr_res.dtype)


@_wraps("numpy.concatenate")
def concatenate(arrays, axis=0):
    """
    For each dimension, uses the metadata of the first array with a non-null
    expression.

    """
    return _concatenate(arrays, axis=axis)


@_wraps("numpy.append")
def append(arr, values, axis=0):
    """
    For each dimension, uses the metadata of `values` if `arr` has no
    expression.

    """
    return _concatenate((arr, values), axis=axis)


######################################################################
# * Fields management

@_wraps("numpy.lib.recfunctions.append_fields")
def append_fields(base, names, data=None, dtypes=None, fill_value=-1):
    """
    The resulting format slightly deviates from NumpPy's to maintain the shape
    and metadata of `base`.

    """
    reference = [base]
    numpy_base = base.view(numpy.ndarray) \
                 if isinstance(base, Data) else base
    if isinstance(data, Data):
        reference += [data]
        numpy_data = data.view(numpy.ndarray).flat
    elif isinstance(data, collections.Iterable) and\
         not isinstance(data, numpy.ndarray):
        reference += data
        numpy_data = []
        for d in data:
            if isinstance(d, Data):
                d = d.view(numpy.ndarray)
            numpy_data.append(d)
    elif data is not None:
        reference += data
        numpy_data = data
    else:
        numpy_data = None

    res = recfunctions.append_fields(
        base=numpy_base, names=names, data=numpy_data,
        dtypes=dtypes, fill_value=fill_value,
        usemask=False, asrecarray=True)

    dims = None
    for arr in reference:
        if isinstance(arr, Data) and \
           functools.reduce(int.__mul__, arr.shape) == functools.reduce(int.__mul__, res.shape):
            dims = arr
            res = res.reshape(arr.shape)
            break
    if dims is None:
        raise ValueError("No input Data matches output shape (%s)" % res.shape)
    return data_array(res, dims=dims)


@_wraps("numpy.lib.recfunctions.drop_fields")
def drop_fields(*args, **kwargs):
    callargs = compat.InspectBind(recfunctions.drop_fields, *args, **kwargs)
    res = recfunctions.drop_fields(*args, **kwargs)
    if (isinstance(callargs.arguments["base"], Data) and
        not callargs.arguments["usemask"] and
        not callargs.arguments["asrecarray"]):
        return data_array(res, dims=callargs.arguments["base"])
    else:
        return res


@_wraps("numpy.lib.recfunctions.merge_arrays")
def merge_arrays(*args, **kwargs):
    callargs = compat.InspectBind(recfunctions.merge_arrays, *args, **kwargs)
    res = recfunctions.merge_arrays(*args, **kwargs)

    if callargs.arguments["usemask"] or callargs.arguments["asrecarray"]:
        return res

    dims = None
    for arr in callargs.arguments["seqarrays"]:
        if isinstance(arr, Data) and \
           functools.reduce(int.__mul__, arr.shape) == functools.reduce(int.__mul__, res.shape):
            dims = arr
            res = res.reshape(arr.shape)
            break
    if dims is None:
        raise ValueError("No input Data matches output shape (%s)" % res.shape)
    return data_array(res, dims=dims)


######################################################################
# * Miscellaneous

@_wraps("numpy.copy")
def copy(*args, **kwargs):
    callargs = compat.InspectBind(numpy.copy, *args, **kwargs)
    try:
        func = callargs.arguments["a"].__class__.copy
    except AttributeError:
        func = numpy.copy
    return func(*args, **kwargs)


@_wraps("numpy.imag")
def imag(*args, **kwargs):
    callargs = compat.InspectBind(numpy.imag, *args, **kwargs)
    try:
        func = callargs.arguments["val"].__class__.imag
    except AttributeError:
        func = numpy.imag
    return func(*args, **kwargs)


@_wraps("numpy.real")
def real(*args, **kwargs):
    callargs = compat.InspectBind(numpy.real, *args, **kwargs)
    try:
        func = callargs.arguments["val"].__class__.real
    except AttributeError:
        func = numpy.real
    return func(*args, **kwargs)


@_wraps("numpy.ravel")
def ravel(*args, **kwargs):
    callargs = compat.InspectBind(numpy.ravel, *args, **kwargs)
    try:
        func = callargs.arguments["a"].__class__.ravel
    except AttributeError:
        func = numpy.ravel
    return func(*args, **kwargs)


@_wraps("numpy.delete")
def delete(*args, **kwargs):
    callargs = compat.InspectBind(numpy.delete, *args, **kwargs)

    _, axis = _get_axis(callargs.arguments["axis"],
                        [callargs.arguments["arr"]])
    callargs.arguments["axis"] = axis

    if callargs.arguments["arr"].ndim > 1 and axis is None:
        callargs.arguments["arr"] = callargs.arguments["arr"].flatten(order="A")

    res = numpy.delete(*callargs.args, **callargs.kwargs)

    arr = callargs.arguments["arr"]
    obj = callargs.arguments["obj"]
    axis = callargs.arguments["axis"]

    if not isinstance(arr, Data):
        return res

    daxis = axis if axis is not None else 0
    obj = arr.dims[daxis]._get_indexes(obj)

    dims = [(dim.expression, dim)
            for dim in arr._dims]
    if axis is None:
        axis = 0
    dims[axis] = (dims[axis][0],
                  list(numpy.delete(list(dims[axis][1]), obj)))
    dims = [meta.Dim(dim[0], dim[1])
            for dim in dims]
    return data_array(res, dims=dims)


__all__ = [
    "append", "concatenate",
    "append_fields", "drop_fields", "merge_arrays",
    "copy", "imag", "real", "ravel",
    "delete",
]
