#!/usr/bin/env python3

import numpy

_real_types = (numpy.int8, numpy.int16, numpy.int32, numpy.int64,
               numpy.float16, numpy.float32, numpy.float64, int, float)


def is_numpy_array_of_reals(x):
    return x.dtype in _real_types if isinstance(x, numpy.ndarray) else False
