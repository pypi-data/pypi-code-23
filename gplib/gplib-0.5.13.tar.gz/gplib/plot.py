# -*- coding: utf-8 -*-
#
#    Copyright 2018 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D

plt.style.use('ggplot')


class Plot(object):

    @staticmethod
    def kernel(kernel, file_name=None):
        """
        Plot a kernel implementation

        :param file_name:
        :type file_name:
        :param kernel:
        :type kernel:
        :return:
        :rtype:
        """
        plt.figure(figsize=(13, 5))
        plt.clf()
        plt.suptitle(kernel.__class__.__name__)
        plt.subplot(121)
        dist = np.linspace(0, 3, 300)[:, None]
        covar = kernel.marginalize_covariance(dist, np.array([[0.0]]))
        covar = covar.reshape(-1)
        plt.plot(dist, covar, 'b-', ms=40)
        plt.xlabel("input, x")
        plt.ylabel("covariance, k(0, x)")

        plt.subplot(122)
        x_grid = np.linspace(-3.0, 3.0, 100)[:, None]
        y_grid = np.linspace(-3.0, 3.0, 100)[:, None]
        covar = kernel.marginalize_covariance(x_grid, y_grid)
        covar = np.flip(covar, 0)
        plt.imshow(
            covar,
            cmap='viridis',
            interpolation='none',
            extent=[-3.0, 3.0, -3.0, 3.0]
        )
        cb = plt.colorbar()
        cb.set_label("covariance, k(x, x')")
        plt.xlabel("input, x")
        plt.ylabel("input, x'")
        if file_name is None:
            plt.show()
        else:
            plt.savefig(file_name, bbox_inches='tight')
            plt.close()

    @staticmethod
    def gp_1d(gp, data, test_data=None, file_name=None):
        """
        Plot gp in 1D

        :param test_data:
        :type test_data:
        :param file_name:
        :type file_name:
        :param data:
        :type data:
        :param gp:
        :type gp:
        :return:
        :rtype:
        """
        plt.figure(figsize=(10, 8))

        show_data, min_values, max_values, diff_values = \
            Plot._get_plot_bounds(data, test_data)

        plot_points = np.arange(
            min_values[0],
            max_values[0],
            diff_values[0] / 500.0
        )[:, None]

        posterior_samples = gp.sample(plot_points, n_samples=10)

        mean = gp.mean_function.marginalize_mean(
            plot_points)

        var = gp.covariance_function.marginalize_covariance(
            plot_points, only_diagonal=True)

        sdev = 3.0 * np.sqrt(var)

        plt.clf()
        plt.plot(
            plot_points.flatten().tolist(),
            posterior_samples, color='#b19df0', linewidth=1
        )
        plt.plot(
            plot_points.flatten().tolist(),
            mean.flatten().tolist(), color='#43dce5', linewidth=2
        )
        plt.plot(
            plot_points.flatten().tolist(),
            (mean - sdev).flatten().tolist(), color='#8091e5',
            linestyle='--', linewidth=2
        )
        plt.plot(
            plot_points.flatten().tolist(),
            (mean + sdev).flatten().tolist(), color='#8091e5',
            linestyle='--', linewidth=2
        )
        plt.plot(
            show_data['X'].flatten().tolist(),
            show_data['Y'].flatten().tolist(), color='#714ce5',
            linestyle='None', marker='o', markersize=4
        )
        if test_data is not None:
            plt.plot(
                test_data['X'].flatten().tolist(),
                test_data['Y'].flatten().tolist(), color='#714ce5',
                linestyle='None', marker='^', markersize=4
            )

        if file_name is None:
            plt.show()
        else:
            plt.savefig(file_name, bbox_inches='tight')
            plt.close()

    @staticmethod
    def gp_2d(gp, data, test_data=None, resolution=40, file_name=None):
        """
        Plot gp in 2D

        :param resolution:
        :type resolution:
        :param test_data:
        :type test_data:
        :param file_name:
        :type file_name:
        :param data:
        :type data:
        :param gp:
        :type gp:
        :return:
        :rtype:
        """
        show_data, min_values, max_values, _ = \
            Plot._get_plot_bounds(data, test_data)

        # Init grid
        x_grid = np.linspace(min_values[0], max_values[0], resolution)
        y_grid = np.linspace(min_values[1], max_values[1], resolution)
        x_grid, y_grid = np.meshgrid(x_grid, y_grid)
        plot_points = np.vstack((x_grid.flatten(), y_grid.flatten())).T

        mean = gp.mean_function.marginalize_mean(
            plot_points)

        # Init plot
        fig = plt.figure()
        axis = fig.gca(projection='3d')

        # plot data
        axis.scatter(
            show_data['X'][:, 0].tolist(),
            show_data['X'][:, 1].tolist(),
            show_data['Y'].tolist(), s=20, color='#000000', marker='o'
        )

        # plot test data
        if test_data is not None:
            axis.scatter(
                test_data['X'][:, 0].tolist(),
                test_data['X'][:, 1].tolist(),
                test_data['Y'].tolist(), s=20, color='#bb00bb', marker='^'
            )

        # plot GP
        z_points = mean
        z_points = z_points.reshape(resolution, resolution)
        axis.plot_surface(
            x_grid, y_grid,
            z_points, rstride=1,
            cstride=1, cmap='viridis', linewidth=0,
            antialiased=False, alpha=0.3
        )

        axis.zaxis.set_major_locator(LinearLocator(10))
        axis.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        if file_name is None:
            plt.show()
        else:
            plt.savefig(file_name, bbox_inches='tight')
            plt.close()

    @staticmethod
    def _get_plot_bounds(data, test_data=None, tail=0.5):
        focus_data = data
        if test_data is not None:
            focus_data = test_data

        points = focus_data['X']
        min_values = np.min(points, axis=0)
        max_values = np.max(points, axis=0)
        diff_values = max_values - min_values
        min_values -= diff_values * tail
        max_values += diff_values * tail
        diff_values = max_values - min_values

        show_i = np.logical_and(
            np.all(min_values < data['X'], axis=1),
            np.all(data['X'] < max_values, axis=1)
        )
        show_data = {
            'X': data['X'][show_i],
            'Y': data['Y'][show_i]
        }

        return show_data, min_values, max_values, diff_values
