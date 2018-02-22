#!/usr/bin/env python

import numpy as np
from abipy.abilab import abiopen
from abipy.tools.numtools import add_periodic_replicas

ncfile = abiopen("si_DEN.nc")
structure = ncfile.structure
red_from_cart = structure.lattice.inv_matrix.T
cart_from_red = structure.lattice.matrix.T

data = add_periodic_replicas(ncfile.density.datar)
nspden, nx, ny, nz = data.shape

xred, yred, zred = np.meshgrid(np.linspace(0, 1, nx), np.linspace(0, 1, ny), np.linspace(0, 1, nz))

#data = data[0, 0, :, :]

import xarray as xr
data = xr.DataArray(data[0], dims=['x', 'y', "z"],
		    coords={'xred': (('x', 'y', "z"), xred),
		            'yred': (('x', 'y', "z"), yred),
		            'zred': (('x', 'y', "z"), zred)})

print(data)

import matplotlib.pyplot as plt
#da = data.sel(z=0)
#da = data.isel(zred=0)
#da.plot.pcolormesh('xred', 'yred')

g_simple = data.plot(x='xred', y='yred', col='zred', col_wrap=4)

#da.plot()
plt.show()




#pcart_list = [ ]
#for iy in range(ny):
#    for iz in range(ny):
#        pred = (0, iy/ny, iz/nz)
#        pcart = np.dot(cart_from_red, pred)
#        pcart_list.append(pcart)
#
#pcart_list = np.reshape(pcart_list, (-1, 3))
#print(pcart_list)

#xcart =
#ycart =
#import xarray as xr
#xr.DataArray(data)
