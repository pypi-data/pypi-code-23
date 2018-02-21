
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # RADOLAN Quick Start

# All RADOLAN composite products can be read by the following function:
# 
# ```python
# data, metadata = wradlib.io.read_RADOLAN_composite("mydrive:/path/to/my/file/filename")
# ```
# 
# Here, ``data`` is a two dimensional integer or float array of shape (number of rows, number of columns). ``metadata`` is a dictionary which provides metadata from the files header section, e.g. using the keys `producttype`, `datetime`, `intervalseconds`, `nodataflag`.
# 
# The [RADOLAN Grid](radolan_grid.ipynb) coordinates can be calculated with [wradlib.georef.get_radolan_grid()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.georef.get_radolan_grid.html).
# 
# With the following code snippet the RW-product is shown in the [Polar Stereographic Projection](radolan_grid.ipynb#Polar-Stereographic-Projection).

# Import modules, filter warnings to avoid cluttering output with DeprecationWarnings and use matplotlib inline or interactive mode if running in ipython or python respectively.

# In[ ]:


import wradlib as wrl
import matplotlib.pyplot as pl
import warnings
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()
import numpy as np


# In[ ]:


# load radolan files
rw_filename = wrl.util.get_wradlib_data_file('radolan/misc/raa01-rw_10000-1408102050-dwd---bin.gz')
rwdata, rwattrs = wrl.io.read_RADOLAN_composite(rw_filename)
# print the available attributes
print("RW Attributes:", rwattrs)


# In[ ]:


# do some masking
sec = rwattrs['secondary']
rwdata.flat[sec] = -9999
rwdata = np.ma.masked_equal(rwdata, -9999)


# In[ ]:


# Get coordinates
radolan_grid_xy = wrl.georef.get_radolan_grid(900,900)
x = radolan_grid_xy[:,:,0]
y = radolan_grid_xy[:,:,1]


# In[ ]:


# plot function
pl.pcolormesh(x, y, rwdata, cmap="spectral")
cb = pl.colorbar(shrink=0.75)
cb.set_label("mm/h")
pl.title('RADOLAN RW Product Polar Stereo \n' + rwattrs['datetime'].isoformat())
pl.grid(color='r')


# A much more comprehensive section using several RADOLAN composites is shown in chapter [RADOLAN Product Showcase](radolan_showcase.ipynb).
