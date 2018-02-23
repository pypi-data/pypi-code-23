
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

import jpype
import numpy as np
import pyconrad

class ImageUtil:

    ########################
    ## Convert Grid/numpy ##
    ########################

    @staticmethod
    def grid_from_numpy(grid):
        return np.ndarray.view(pyconrad.PyGrid.from_numpy(grid))

    @staticmethod
    def numpy_from_grid(ndarray):
        return np.ndarray.view(pyconrad.PyGrid.from_grid(ndarray))

    #################
    ## Save Images ##
    #################

    @staticmethod
    def save_grid_as_tiff(grid, path):
        jpype.JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    @staticmethod
    def save_numpy_as_tiff(array, path):
        grid = ImageUtil.grid_from_numpy(array)
        jpype.JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    #################
    ## Load Images ##
    #################

    @staticmethod
    def grid_from_tiff(path):
        ij = jpype.JPackage('ij').IJ.openImage(path)
        if not ij:
            raise RuntimeError('Error opening file \'%s\'' % path)
        grid = jpype.JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(ij)
        return grid

    @staticmethod
    def array_from_tiff(path):
        ij = jpype.JPackage('ij').IJ.openImage(path)
        if not ij:
            raise RuntimeError('Error opening file \'%s\'' % path)
        grid = jpype.JPackage('edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(ij)
        return ImageUtil.numpy_from_grid(grid)

