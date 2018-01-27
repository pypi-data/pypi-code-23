# This package exists for compatibility with previous releases
# of ScientificPython that supported both NumPy and the old
# Numeric package. Please don't use it in new code, use numpy
# directly.

from oldnumeric import *
from numpy import ndarray as array_type

def int_sum(a, axis=0):
    return add.reduce(a, axis)
def zeros_st(shape, other):
    return zeros(shape, dtype=other.dtype)

package = "NumPy"
