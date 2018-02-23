import numpy as np
from pyconrad import PyConrad

def wrapGrid1D(grid1D):
    array = np.array(grid1D.getBuffer()[:])
    return array



def wrapGrid2D(grid2D):
    w = grid2D.getWidth()
    h = grid2D.getHeight()
    array = np.array(grid2D.getBuffer()[:])
    array = np.reshape(array, [h, w])

    return array



def wrapGrid3D(grid3D):
    size = grid3D.getSize()
    array = np.zeros((size[2], size[1], size[0]))
    for id in range(size[2]):
        subgrid = grid3D.getSubGrid(id)
        array[id, ...] = wrapGrid2D(subgrid)
    return array



def wrapGrid4D(grid4D):
    size = grid4D.getSize()
    array = np.zeros([size[3], size[2], size[1], size[0]])
    for f in range(size[3]):
        subgrid = grid4D.getSubGrid(f)
        array[f, ...] = wrapGrid3D(subgrid)
    return array



def wrapNumpyArrayToGrid1D(array):
    grid = PyConrad.get_instance().classes.stanford.rsl.conrad.data.numeric.Grid1D(array)
    return grid



def wrapNumpyArrayToGrid2D(array):
    dim = array.shape
    flattened = array.flatten()
    grid = PyConrad.get_instance().classes.stanford.rsl.conrad.data.numeric.Grid2D(flattened, dim[1], dim[0])
    return grid



def wrapNumpyArrayToGrid3D(array):
    dim = array.shape
    grid = PyConrad.get_instance().classes.stanford.rsl.conrad.data.numeric.Grid3D(dim[2], dim[1], dim[0])
    for id in range(dim[0]):
        subgrid = wrapNumpyArrayToGrid2D(array[id, ...])
        grid.setSubGrid(id, subgrid)
    return grid



def wrapNumpyArrayToGrid4D(array):
    dim = array.shape
    grid = PyConrad.get_instance().classes.stanford.rsl.conrad.data.numeric.Grid4D(dim[3], dim[2], dim[1], dim[0],
                                                                                   False)
    for id in range(dim[0]):
        subgrid = wrapNumpyArrayToGrid3D(array[id, ...])
        grid.setSubGrid(id, subgrid)
    return grid
