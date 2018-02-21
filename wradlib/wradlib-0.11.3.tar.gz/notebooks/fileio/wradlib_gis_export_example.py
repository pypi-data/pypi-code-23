
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # Export a dataset in GIS-compatible format
# 
# In this notebook, we demonstrate how to export a gridded dataset in GeoTIFF and ESRI ASCII format. This will be exemplified using RADOLAN data from the German Weather Service.

# In[ ]:


import wradlib as wrl
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# ### Step 1: Read the original data

# In[ ]:


# We will export this RADOLAN dataset to a GIS compatible format
wdir = wrl.util.get_wradlib_data_path() + '/radolan/grid/'
filename = 'radolan/misc/raa01-sf_10000-1408102050-dwd---bin.gz'
filename = wrl.util.get_wradlib_data_file(filename)
data_raw, meta = wrl.io.read_RADOLAN_composite(filename)


# ### Step 2: Get the projected coordinates of the RADOLAN grid

# In[ ]:


# This is the RADOLAN projection
proj_osr = wrl.georef.create_osr("dwd-radolan")

# Get projected RADOLAN coordinates for corner definition
xy_raw = wrl.georef.get_radolan_grid(900, 900)


# ### Step 3: Check Origin and Row/Column Order
# 
# We know, that `wrl.read_RADOLAN_composite` returns a 2D-array (rows, cols) with the origin in the lower left corner. Same applies to `wrl.georef.get_radolan_grid`. For the next step, we need to flip the data and the coords up-down. The coordinate corner points also need to be adjusted from lower left corner to upper right corner.

# In[ ]:


data, xy = wrl.georef.set_raster_origin(data_raw, xy_raw, 'upper')


# ### Step 4a: Export as GeoTIFF
# 
# For RADOLAN grids, this projection will probably not be recognized by
# ESRI ArcGIS.

# In[ ]:


# create 3 bands
data = np.stack((data, data+100, data+1000))
ds = wrl.georef.create_raster_dataset(data, xy, projection=proj_osr)
wrl.io.write_raster_dataset(wdir + "geotiff.tif", ds, 'GTiff')


# ### Step 4b: Export as ESRI ASCII file (aka Arc/Info ASCII Grid)

# In[ ]:


# Export to Arc/Info ASCII Grid format (aka ESRI grid)
#     It should be possible to import this to most conventional
# GIS software.
# only use first band
proj_esri = proj_osr.Clone()
proj_esri.MorphToESRI()
ds = wrl.georef.create_raster_dataset(data[0], xy, projection=proj_esri)
wrl.io.write_raster_dataset(wdir + "aaigrid.asc", ds, 'AAIGrid', options=['DECIMAL_PRECISION=2'])


# ### Step 5a: Read from GeoTIFF

# In[ ]:


ds1 = wrl.io.open_raster(wdir + "geotiff.tif")
data1, xy1, proj1 = wrl.georef.extract_raster_dataset(ds1, nodata=-9999.)
np.testing.assert_array_equal(data1, data)
np.testing.assert_array_equal(xy1[:-1,:-1,:], xy)


# ### Step 5b: Read from ESRI ASCII file (aka Arc/Info ASCII Grid)

# In[ ]:


ds2 = wrl.io.open_raster(wdir + "aaigrid.asc")
data2, xy2, proj2 = wrl.georef.extract_raster_dataset(ds2, nodata=-9999.)
np.testing.assert_array_almost_equal(data2, data[0], decimal=2)
np.testing.assert_array_almost_equal(xy2[:-1,:-1,:], xy)

