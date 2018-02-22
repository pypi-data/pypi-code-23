#!/usr/bin/env python
"""
This example shows how to plot a band structure
"""
from abipy.abilab import abiopen
import abipy.data as abidata

with abiopen(abidata.ref_file("mgb2_kmesh181818_FATBANDS.nc")) as fbnc_kmesh:
    ebands = fbnc_kmesh.ebands
    #ebands.to_bxsf("mgb2.bxsf")
    #ebands.boxplot()
    #ebands = ebands.interpolate(kmesh=[40, 40, 40]).ebands_kmesh

    #from mayavi import mlab
    #mlab.options.offscreen = True
    #ebands.mvplot_isosurfaces(show=True)

    eb3d = ebands.get_ebands3d()
    #eb3d.plot_isosurfaces()
    eb3d.mvplot_isosurfaces()
    #eb3d.mvplot_cutplanes(band=4)

    #arr = mlab.screenshot()
    #import matplotlib.pyplot as plt
    #plt.imshow(arr)
    #plt.axis('off')
    #plt.show()
