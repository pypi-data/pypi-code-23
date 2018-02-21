
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# In[ ]:


# flake8: noqa


# # Routine verification measures for radar-based precipitation estimates

# In[ ]:


import wradlib
import os
import numpy as np
import matplotlib.pyplot as pl
import warnings
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()


# ## Extract bin values from a polar radar data set at rain gage locations

# #### Read polar data set

# In[ ]:


filename = wradlib.util.get_wradlib_data_file('misc/polar_R_tur.gz')
data = np.loadtxt(filename)


# #### Define site coordinates (lon/lat) and polar coordinate system

# In[ ]:


r = np.arange(1,129)
az = np.linspace(0,360,361)[0:-1]
sitecoords = (9.7839, 48.5861)


# #### Make up two rain gauge locations (say we want to work in Gaus Krueger zone 3)

# In[ ]:


# Define the projection via epsg-code
proj = wradlib.georef.epsg_to_osr(31467)
# Coordinates of the rain gages in Gauss-Krueger 3 coordinates
x, y = np.array([3557880, 3557890]), np.array([5383379, 5383375])


# #### Now extract the radar values at those bins that are closest to our rain gauges
# 
# For this purppose, we use the PolarNeighbours class from wraldib's verify module. Here, we extract the 9 nearest bins...

# In[ ]:


polarneighbs = wradlib.verify.PolarNeighbours(r, az, sitecoords, proj, x, y, nnear=9)
radar_at_gages = polarneighbs.extract(data)
print( "Radar values at rain gauge #1: %r" % radar_at_gages[0].tolist())
print( "Radar values at rain gauge #2: %r" % radar_at_gages[1].tolist())


# #### Retrieve the bin coordinates (all of them or those at the rain gauges)

# In[ ]:


binx, biny = polarneighbs.get_bincoords()
binx_nn, biny_nn = polarneighbs.get_bincoords_at_points()


# #### Plot the entire radar domain and zoom into the surrounding of the rain gauge locations

# In[ ]:


fig = pl.figure(figsize=(12,12))
ax = fig.add_subplot(121)
ax.plot(binx, biny, 'r+')
ax.plot(binx_nn, biny_nn, 'b+', markersize=10)
ax.plot(x, y, 'bo')
ax.axis('tight')
ax.set_aspect("equal")
pl.title("Full view")
ax = fig.add_subplot(122)
ax.plot(binx, biny, 'r+')
ax.plot(binx_nn, biny_nn, 'b+', markersize=10)
ax.plot(x, y, 'bo')
pl.xlim(binx_nn.min()-5, binx_nn.max()+5)
pl.ylim(biny_nn.min()-7, biny_nn.max()+8)
ax.set_aspect("equal")
txt = pl.title("Zoom into rain gauge locations")
pl.tight_layout()


# ## Create a verification report
# 
# In this example, we make up a true Kdp profile and verify our reconstructed Kdp.

# #### Create synthetic data and reconstruct KDP

# In[ ]:


# Synthetic truth
dr = 0.5
r = np.arange(0, 100, dr)
kdp_true = np.sin(0.3*r)
kdp_true[kdp_true<0] = 0.
phidp_true = np.cumsum(kdp_true)*2*dr
# Synthetic observation of PhiDP with a random noise and gaps
phidp_raw = phidp_true + np.random.uniform(-2, 2, len(phidp_true))
gaps = np.random.uniform(0, len(r), 20).astype("int")
phidp_raw[gaps] = np.nan

# Reconstruct PhiDP and KDP
phidp_re, kdp_re = wradlib.dp.process_raw_phidp_vulpiani(phidp_raw, dr=dr)

# Plot results
fig = pl.figure(figsize=(12,8))
ax = fig.add_subplot(211)
pl.plot(kdp_true, "g-", label="True KDP")
pl.plot(kdp_re, "r-", label="Reconstructed KDP")
pl.grid()
lg = pl.legend()

ax = fig.add_subplot(212)
pl.plot(r, phidp_true, "b--", label="True PhiDP")
pl.plot(r, np.ma.masked_invalid(phidp_raw), "b-", label="Raw PhiDP")
pl.plot(r, phidp_re, "g-", label="Reconstructed PhiDP")
pl.grid()
lg = pl.legend(loc="lower right")
txt = pl.xlabel("Range (km)")


# #### Create verification report

# In[ ]:


metrics = wradlib.verify.ErrorMetrics(kdp_true, kdp_re)
metrics.pprint() 
ax = metrics.plot()
xlabel = ax.set_xlabel("True KDP (deg/km)")
ylabel = ax.set_ylabel("Reconstructed KDP (deg/km)")

