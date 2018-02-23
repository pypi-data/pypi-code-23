import pyconrad.autoinit
import numpy as np


def test_swapaxes():
    original_array = np.random.randn(50,30,20).astype(pyconrad.java_float_dtype)
    swapped_axes = np.swapaxes(original_array, 1,2)

    grid = pyconrad.PyGrid.from_numpy(original_array).grid
    rtn = pyconrad.PyGrid.from_grid(grid)
    assert np.allclose(original_array,rtn)

    grid = pyconrad.PyGrid.from_numpy(swapped_axes).grid
    rtn = pyconrad.PyGrid.from_grid(grid)
    assert np.allclose(swapped_axes,rtn)


