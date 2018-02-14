import logging

import numpy as np

from pyezzi.laplace import solve_3D as laplace_solver
from pyezzi.yezzi import iterative_relaxation_3D as yezzi_solver


class ThicknessSolver:
    def __init__(self,
                 labeled_image,
                 spacing=None,
                 label_inside=1,
                 label_wall=2,
                 label_holes=3,
                 laplace_tolerance=1e-6,
                 laplace_max_iter=5000,
                 yezzi_tolerance=1e-6,
                 yezzi_max_iter=5000,
                 run=True):
        log.debug("Instantiating ThicknessSolver")
        if spacing is None:
            spacing = np.array([1.0, 1.0, 1.0])
        else:
            spacing = np.array(spacing, float)
        self.spacing = spacing

        self.dtype = np.float32

        labeled_image = np.pad(labeled_image, 1, 'constant')

        self.original_shape = labeled_image.shape

        cropped_image, limits = crop_img(labeled_image)
        self.cropped_shape = cropped_image.shape
        self.limits = limits

        # Using cardiac terminology here...
        self.partial_wall = (cropped_image == label_wall)
        self.holes = (cropped_image == label_holes)
        self.wall = self.partial_wall | self.holes

        self.endo = cropped_image == label_inside
        self.epi = self.wall | self.endo

        self.laplace_tolerance = laplace_tolerance
        self.laplace_max_iter = laplace_max_iter
        self.yezzi_tolerance = yezzi_tolerance
        self.yezzi_max_iter = yezzi_max_iter

        self._flatten_wall()

        if run:
            self._solve_laplacian()
            self._solve_thickness()
        else:
            self.cropped_laplace_grid = None
            self.laplacian_iterations = None
            self.laplacian_max_error = None
            self.cropped_L0 = None
            self.cropped_L1 = None
            self.cropped_thickness = None

    def _flatten_wall(self):
        (self.wall_idx_i,
         self.wall_idx_j,
         self.wall_idx_k) = np.argwhere(self.wall).T
        (self.partial_wall_idx_i,
         self.partial_wall_idx_j,
         self.partial_wall_idx_k) = np.argwhere(self.partial_wall).T

    def _solve_laplacian(self):
        init = np.zeros_like(self.wall, float)
        init[np.logical_not(self.epi)] = 1
        log.info("Solving Laplacian...")
        laplace_grid, iterations, max_error = laplace_solver(
            self.wall_idx_i,
            self.wall_idx_j,
            self.wall_idx_k,
            init,
            self.laplace_tolerance,
            self.laplace_max_iter,
            self.spacing)
        log.debug(
            f"Laplacian: {iterations} iterations, max_error = {max_error}")
        self.cropped_laplace_grid = laplace_grid
        self.laplacian_iterations = iterations
        self.laplacian_max_error = max_error
        log.debug("Computing tangent vector field")
        self._gradients = np.array(np.gradient(self.cropped_laplace_grid))

        for i, spacing in enumerate(self.spacing):
            self._gradients[i] /= spacing

        self._gradients /= np.sqrt(self._gradients[0] ** 2
                                   + self._gradients[1] ** 2
                                   + self._gradients[2] ** 2)

    def _restore_cropped_image(self, image):
        return restore_cropped_img(image,
                                   self.limits,
                                   self.original_shape)[1:-1, 1:-1, 1:-1]

    def _solve_thickness(self):
        if self.cropped_laplace_grid is None:
            self._solve_laplacian()

        log.info("Computing L0 and L1...")

        L0, L1, iterations, max_error = yezzi_solver(
            self.partial_wall_idx_i,
            self.partial_wall_idx_j,
            self.partial_wall_idx_k,
            self._gradients,
            self.yezzi_tolerance,
            self.yezzi_max_iter,
            self.spacing,
            self.cropped_shape)
        log.debug(
            f"Thickness computation: {iterations} iterations, "
            f"max_error = {max_error}")

        self.cropped_L0 = L0
        self.cropped_L1 = L1
        self.cropped_thickness = L0 + L1

    @property
    def tangent_vectors(self):
        if self._gradients is None:
            self._solve_laplacian()
        res = np.zeros(tuple(i - 2 for i in self.original_shape) + (3,),
                       np.float)
        wall = self._restore_cropped_image(self.wall)
        res[wall] = np.moveaxis(self._gradients, 0, -1)[self.wall]
        return res

    @property
    def result(self):
        if self.cropped_thickness is None:
            self._solve_thickness()
        return self._restore_cropped_image(self.cropped_thickness)

    @property
    def L0(self):
        if self.cropped_thickness is None:
            self._solve_thickness()
        return self._restore_cropped_image(self.cropped_L0)

    @property
    def L1(self):
        if self.cropped_thickness is None:
            self._solve_thickness()
        return self._restore_cropped_image(self.cropped_L1)

    @property
    def laplace_grid(self):
        if self.cropped_laplace_grid is None:
            self._solve_laplacian()
        return self._restore_cropped_image(self.cropped_laplace_grid)


def compute_thickness(labeled_image,
                      spacing=None,
                      label_inside=1,
                      label_wall=2,
                      label_holes=3,
                      laplace_tolerance=1e-6,
                      laplace_max_iter=5000,
                      yezzi_tolerance=1e-6,
                      yezzi_max_iter=5000):
    """
    Returns wall thicknesses computed with Yezzi's method

    Easy-to-use, functionnal interface to the ThicknessSolver class.

    Input image must be labeled as specified
    (background=0, inside=1, wall=2, holes=3 by default)

    :param labeled_image:np.ndarray
    Labeled image defined of ints
    :param spacing:iterable, optional
    Defines the spacing between voxels along the 3 axes. 1, 1, 1 by default
    :param label_inside:int, optional
    The label of the object's interior
    :param label_wall:int, optional
    The label of the object's wall
    :param label_holes:int, optional
    The label of the holes in the object's wall
    :param laplace_tolerance:float, optional
    Maximum error allowed for Laplacian resolution
    :param laplace_max_iter:int, optional
    Maximum iterations allowed for Laplacian resolution
    :param yezzi_tolerance:float, optional
    Maximum error allowed for thickness computation
    :param yezzi_max_iter:int, optional
    Maximum iterations allowed for thickness computation
    :return:np.ndarray
    Array of floats, representing thickness at each wall point
    """

    solver = ThicknessSolver(labeled_image,
                             spacing,
                             label_inside,
                             label_wall,
                             label_holes,
                             laplace_tolerance,
                             laplace_max_iter,
                             yezzi_tolerance,
                             yezzi_max_iter)

    return solver.result


def crop_img(nda_image, margins=1):
    """
    Crops the blank part of a 3D mask

    :param nda_image:np.array
    :param margins:int
    :return:
    """
    min_slice, max_slice = np.argwhere(nda_image.sum(axis=(1, 2)))[[0, -1]]
    min_row, max_row = np.argwhere(nda_image.sum(axis=(0, 2)))[[0, -1]]
    min_col, max_col = np.argwhere(nda_image.sum(axis=(0, 1)))[[0, -1]]
    min_row -= margins
    min_col -= margins
    min_slice -= margins
    max_row += margins
    max_col += margins
    max_slice += margins
    min_slice, max_slice, min_row, max_row, min_col, max_col = \
        [int(x) for x in
         (min_slice,
          max_slice,
          min_row,
          max_row,
          min_col,
          max_col)]
    cropped_img = nda_image[
                  min_slice:max_slice,
                  min_row:max_row,
                  min_col:max_col]

    limits = (min_slice, max_slice,
              min_row, max_row,
              min_col, max_col)

    return cropped_img, limits


def restore_cropped_img(image, limits, original_shape):
    return np.pad(image,
                  ((limits[0], original_shape[0] - limits[1]),
                   (limits[2], original_shape[1] - limits[3]),
                   (limits[4], original_shape[2] - limits[5])),
                  mode="constant")


log = logging.getLogger(__name__)
