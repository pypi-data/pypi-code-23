
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # Computing cartesian and geographical coordinates for polar data

# In[ ]:


import numpy as np
import wradlib.georef as georef
import wradlib.io as io
import wradlib.util as util
import warnings
warnings.filterwarnings('ignore')


# ## Read the data
# 
# Here, we use an OPERA hdf5 dataset.

# In[ ]:


filename = 'hdf5/20130429043000.rad.bewid.pvol.dbzh.scan1.hdf'
filename = util.get_wradlib_data_file(filename)
pvol = io.read_OPERA_hdf5(filename)


# ## Count the number of datasets

# In[ ]:


ntilt = 1
for i in range(100):
    try:
        pvol["dataset%d/what" % ntilt]
        ntilt += 1
    except Exception:
        ntilt -= 1
        break


# ## Define radar location and scan geometry

# In[ ]:


nrays = int(pvol["dataset1/where"]["nrays"])
nbins = int(pvol["dataset1/where"]["nbins"])
rscale = int(pvol["dataset1/where"]["rscale"])
coord = np.empty((ntilt, nrays, nbins, 3))
for t in range(ntilt):
    elangle = pvol["dataset%d/where" % (t + 1)]["elangle"]
    coord[t, ...] = georef.sweep_centroids(nrays, rscale, nbins, elangle)
# ascale = math.pi / nrays
sitecoords = (pvol["where"]["lon"], pvol["where"]["lat"],
              pvol["where"]["height"])
print(coord.shape)


# ## Retrieve azimuthal equidistant coordinates and projection

# In[ ]:


coords, proj_radar = georef.spherical_to_xyz(coord[..., 0],
                                             np.degrees(coord[..., 1]),
                                             coord[..., 2], sitecoords)
test = coords[0, 90, 0:960:60, 0]
print(test)


# ## Retrieve geographic coordinates (longitude and latitude)

# ### Using convenience function *spherical_to_proj*.

# In[ ]:


lonlatalt = georef.spherical_to_proj(coord[..., 0],
                                     np.degrees(coord[..., 1]),
                                     coord[..., 2], sitecoords)
test = lonlatalt[0, 90, 0:960:60, 0]
print(test)


# ### Using reproject

# In[ ]:


lonlatalt1 = georef.reproject(coords, projection_source=proj_radar,
                             projection_target=georef.get_default_projection())

test = lonlatalt1[0, 90, 0:960:60, 0]
print(test)

