#!/usr/bin/env python
import matplotlib.pyplot as plt

from abipy.tools.plotting import (set_axlims, add_fig_kwargs, get_ax_fig_plt, get_axarray_fig_plt,
    get_ax3d_fig_plt, rotate_ticklabels, plot_unit_cell, Slideshow)

if __name__ == "__main__":
    #with Slideshow(slide=False, timeout=5) as s:
    with Slideshow(slide=True, timeout=5) as s:
        ax1, fig1, plt = get_ax_fig_plt(ax=None)
        ax1.plot([1, 2, 3])
        s(fig1)
        #fig1.draw()

        ax2, fig2, _ = get_ax_fig_plt(ax=None)
        ax2.plot([0, 0, 3])
        s(fig2)
        #fig2.show()
        #plt.show()