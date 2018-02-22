#!/usr/bin/env python
"""
This example shows how to plot a band structure
"""
from abipy.abilab import abiopen
import abipy.data as abidata

with abiopen(abidata.ref_file("si_scf_GSR.nc")) as ncfile:
    ebands = ncfile.ebands
    ebands = ebands.interpolate(kmesh=(24, 24, 24)).ebands_kmesh

    eb3d = ebands.get_ebands3d()
    eb3d.plot_contour(band=3) #, levels=[-0.3, -0.2, -0.1])
    #eb3d.mvplot_isosurfaces()
