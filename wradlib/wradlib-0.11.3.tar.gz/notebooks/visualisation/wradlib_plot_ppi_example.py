
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # A simple function to plot polar data in cartesian coordinate systems

# In[ ]:


import numpy as np
import matplotlib.pyplot as pl
import wradlib
import warnings
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()


# ### Read a polar data set from the German Weather Service

# In[ ]:


filename = wradlib.util.get_wradlib_data_file('dx/raa00-dx_10908-0806021735-fbg---bin.gz')
img, meta = wradlib.io.readDX(filename)


# Inspect the data set a little

# In[ ]:


print("Shape of polar array: %r\n" % (img.shape,))
print("Some meta data of the DX file:")
print("\tdatetime: %r" % (meta["datetime"],))
print("\tRadar ID: %s" % (meta["radarid"],))


# ### The simplest way to plot this dataset

# In[ ]:


wradlib.vis.plot_ppi(img)
txt = pl.title('Simple PPI')


# ### Plotting just one sector

# For this purpose, we need to give the ranges and azimuths explicitly...

# In[ ]:


r = np.arange(40, 81)
az = np.arange(200, 251)
ax, pm = wradlib.vis.plot_ppi(img[200:250, 40:80], r, az, autoext=False)
txt = pl.title('Sector PPI')


# *Notice we passed one more range value and azimuth angle as we passed actual data. Otherwise the last row and column of our data would not be plotted.*

# ### Adding a crosshair to the PPI 

# In[ ]:


# We introduce a site offset...
site = (10., 45.)
wradlib.vis.plot_ppi(img, site=site)
# ... plot a crosshair over our data...
wradlib.vis.plot_ppi_crosshair(site=site, ranges=[50, 100, 128], 
                               angles=[0, 90, 180, 270], 
                               line=dict(color='white'), 
                               circle={'edgecolor': 'white'})
pl.title('Offset and Custom Crosshair')
pl.axis("tight")
pl.axes().set_aspect('equal')


# ### Placing the polar data in a projected Cartesian reference system

# Using the `proj` keyword we tell the function to:
# - interpret the site coordinates as longitude/latitude
# - reproject the coordinates to the given projection (here: dwd-radolan composite coordinate system)

# In[ ]:


site=(10., 45., 0)
proj_rad = wradlib.georef.create_osr("dwd-radolan")
ax, pm = wradlib.vis.plot_ppi(img, site=site, proj=proj_rad)
# Now the crosshair ranges must be given in meters
wradlib.vis.plot_ppi_crosshair(site=site,
                               ranges=[40000, 80000, 128000],
                               line=dict(color='white'),
                               circle={'edgecolor':'white'},
                               proj=proj_rad
                               )
pl.title('Georeferenced/Projected PPI')
pl.axis("tight")
pl.axes().set_aspect('equal')


# ### Some side effects of georeferencing

# Transplanting the radar virtually moves it away from the central meridian of the projection (which is 10 degrees east). Due north now does not point straight upwards on the map.
# 
# The crosshair shows this: for the case that the lines should actually become curved, they are implemented as a piecewise linear curve with 10 vertices. The same is true for the range circles, but with more vertices, of course.

# In[ ]:


site=(45., 7.)
ax, pm = wradlib.vis.plot_ppi(img, site=site, proj=proj_rad)
ax = wradlib.vis.plot_ppi_crosshair(site=site,
                               ranges=[64000, 128000],
                               line=dict(color='red'),
                               circle={'edgecolor': 'red'},
                               proj=proj_rad
                               )
txt = pl.title('Projection Side Effects')


# ### More decorations and annotations

# You can annotate these plots by using standard matplotlib methods.

# In[ ]:


ax, pm = wradlib.vis.plot_ppi(img)
ylabel = ax.set_xlabel('easting [km]')
ylabel = ax.set_ylabel('northing [km]')
title = ax.set_title('PPI manipulations/colorbar')
# you can now also zoom - either programmatically or interactively
xlim = ax.set_xlim(-80, -20)
ylim = ax.set_ylim(-80, 0)
# as the function returns the axes- and 'mappable'-objects colorbar needs, adding a colorbar is easy
cb = pl.colorbar(pm, ax=ax)

