
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # RADOLAN Grid

# ## Polar Stereographic Projection

# The projected composite raster is equidistant with a grid-spacing of 1.0 km in most cases. There are composites which have 2.0 km grid-spacing (e.g. PC).
# 
# There are three different grid sizes, the well-known 900 rows by 900 columns (normal), 1500 rows by 1400 columns (extended, european) and 460 rows by 460 columns (small).
# 
# Common to all is that the plane of projection intersects the earth sphere at $\phi_0 = 60.0^{\circ}N$. The cartesian co-ordinate system is aligned parallel to the $\lambda_0 = 10.0^{\circ}E$ meridian.
# 
# The reference point ($\lambda_m$, $\phi_m$) is $9.0^{\circ}E$ and $51.0^{\circ}N$, which is the center of the two smaller grids. The extended grid has an offset in respect to this reference point of 350km by 150km.
# 
# The earth as sphere with an radius of 6370.04 km is used for all calculations.
# 
# With formulas (1), (2) and (3) the geographic reference points ($\lambda$, $\phi$) can be converted to projected cartesian coordinates. The calculated (x y) is the distance vector to the origign of the cartesian coordinate system (north pole).
# 
# $\begin{equation}
# x = R * M(\phi) * cos(\phi) * sin(\lambda - \lambda_0)
# \tag{1}
# \end{equation}$
# 
# $\begin{equation}
# y = -R * M(\phi) * cos(\phi) * cos(\lambda - \lambda_0)
# \tag{2}
# \end{equation}$
# 
# $\begin{equation}
# M(\phi) =  \frac {1 + sin(\phi_0)} {1 + sin(\phi)}
# \tag{3}
# \end{equation}$
# 
# Assumed the point ($10.0^{\circ}E$, $90.0^{\circ}N$) is defined as coordinate system origin. Then all ccordinates can be calculated with the known grid-spacing d as:
# 
# $\begin{equation}
# x = x_0 + d * (j - j_0)
# \tag{4}
# \end{equation}$
# 
# $\begin{equation}
# y = y_0 + d * (i - i_0)
# \tag{5}
# \end{equation}$
# 
# with i, j as cartesian indices.
# 
# $\omega radlib$ provides the convenience function [wradlib.georef.get_radolan_grid()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.georef.get_radolan_grid.html) which returns the radolan grid for further processing. It takes `nrows` and `ncols` as parameters and returns the projected cartesian coordinates or the wgs84 coordinates (keyword arg wgs84=True) as numpy ndarray (nrows x ncols x 2).

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


radolan_grid_xy = wrl.georef.get_radolan_grid(900,900)
print("{0}, ({1:.4f}, {2:.4f})".format(radolan_grid_xy.shape, *radolan_grid_xy[0,0,:]))


# In[ ]:


radolan_grid_ll = wrl.georef.get_radolan_grid(900,900, wgs84=True)
print("{0}, ({1:.4f}, {2:.4f})".format(radolan_grid_ll.shape, *radolan_grid_ll[0,0,:]))


# ## Inverse Polar Stereographic Projection

# The geographic coordinates of specific datapoints can be calculated by using the cartesian coordinates (x,y) and the following formulas:
# 
# $\begin{equation}
# \lambda = \arctan\left(\frac {-x} {y}\right) + \lambda_0
# \tag{6}
# \end{equation}$
#    
# $\begin{equation}
# \phi = \arcsin\left(\frac {R^2 * \left(1 + \sin\phi_0\right)^2 - \left(x^2 + y^2\right)} {R^2 * \left(1 + \sin\phi_0\right)^2 + \left(x^2 + y^2\right)}\right)
# \tag{7}
# \end{equation}$

# ## Standard Formats

# ### WKT-String

# The German Weather Service provides a [WKT-string](https://kunden.dwd.de/geoserver/web/?wicket:bookmarkablePage=:org.geoserver.web.demo.SRSDescriptionPage&code=EPSG:1000001). This WKT (well known text) is used to create the osr-object representation of the radolan projection.
# 
# For the scale_factor the intersection of the projection plane with the earth sphere at $60.0^{\circ}N$ has to be taken into account:
# 
# $\begin{equation}
# scale\_factor = \frac {1 + \sin\left(60.^{\circ}\right)} {1 + \sin\left(90.^{\circ}\right)} = 0.93301270189
# \tag{8}
# \end{equation}$
# 
# Also, the `PROJECTION["Stereographic_North_Pole"]` isn't known within GDAL/OSR. It has to be changed to the known `PROJECTION["polar_stereographic"]`.
# 
# With these adaptions we finally yield the Radolan Projection as WKT-string. This WKT-string is used within $\omega radlib$ to create the osr-object by using the helper-function [wradlib.georef.create_osr()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.georef.create_osr.html).

# In[ ]:


proj_stereo = wrl.georef.create_osr("dwd-radolan")
print(proj_stereo)


# ### PROJ.4

# Using the above WKT-String the PROJ.4 representation can be derived as:
# 
# ```python
#     +proj=stere +lat_0=90 +lat_ts=90 +lon_0=10 +k=0.93301270189
#     +x_0=0 +y_0=0 +a=6370040 +b=6370040 +to_meter=1000 +no_defs
# ```
# 
# This PROJ.4-string can also be used to create the osr-object by using the helper-function [wradlib.georef.proj4_to_osr()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.georef.proj4_to_osr.html):

# In[ ]:


# create radolan projection osr object
dwd_string = ('+proj=stere +lat_0=90 +lat_ts=90 +lon_0=10 +k=0.93301270189' 
              '+x_0=0 +y_0=0 +a=6370040 +b=6370040 +to_meter=1000 +no_defs')
proj_stereo = wrl.georef.proj4_to_osr(dwd_string)
print(proj_stereo)


# ## Grid Reprojection

# Within $\omega radlib$ the [wradlib.georef.reproject()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.georef.reproject.html) function can be used to convert the radolan grid data from xy-space to lonlat-space and back. First, we need to create the necessary Spatial Reference Objects for the RADOLAN-projection and wgs84.

# In[ ]:


from osgeo import osr
proj_stereo = wrl.georef.create_osr("dwd-radolan")
proj_wgs = osr.SpatialReference()
proj_wgs.ImportFromEPSG(4326)
print(proj_wgs)


# Then, we call `reproject` with the osr-objects as `projection_source` and `projection_target` parameters.

# In[ ]:


radolan_grid_ll = wrl.georef.reproject(radolan_grid_xy, projection_source=proj_stereo, projection_target=proj_wgs)
print("{0}, ({1:.4f}, {2:.4f})".format(radolan_grid_ll.shape, *radolan_grid_ll[0,0,:]))


# And the other way round.

# In[ ]:


radolan_grid_xy = wrl.georef.reproject(radolan_grid_ll, projection_source=proj_wgs, projection_target=proj_stereo)
print("{0}, ({1:.4f}, {2:.4f})".format(radolan_grid_xy.shape, *radolan_grid_xy[0,0,:]))


# In the following example the RADOLAN grid is projected to wgs84 and GaussKrüger Zone3.

# In[ ]:


# create Gauss Krueger zone 3 projection osr object
proj_gk3 = osr.SpatialReference()
proj_gk3.ImportFromEPSG(31467)

# transform radolan polar stereographic projection to wgs84 and then to gk3
radolan_grid_ll = wrl.georef.reproject(radolan_grid_xy,
                                       projection_source=proj_stereo,
                                       projection_target=proj_wgs)
radolan_grid_gk = wrl.georef.reproject(radolan_grid_ll,
                                       projection_source=proj_wgs,
                                       projection_target=proj_gk3)

lon_wgs0 = radolan_grid_ll[:, :, 0]
lat_wgs0 = radolan_grid_ll[:, :, 1]

x_gk3 = radolan_grid_gk[:, :, 0]
y_gk3 = radolan_grid_gk[:, :, 1]

x_rad = radolan_grid_xy[:, :, 0]
y_rad = radolan_grid_xy[:, :, 1]

print("\n------------------------------")
print("source radolan x,y-coordinates")
print(u"       {0}      {1} ".format('x [km]', 'y [km]'))
print("ll: {:10.4f} {:10.3f} ".format(x_rad[0, 0], y_rad[0, 0]))
print("lr: {:10.4f} {:10.3f} ".format(x_rad[0, -1], y_rad[0, -1]))
print("ur: {:10.4f} {:10.3f} ".format(x_rad[-1, -1], y_rad[-1, -1]))
print("ul: {:10.4f} {:10.3f} ".format(x_rad[-1, 0], y_rad[-1, 0]))
print("\n--------------------------------------")
print("transformed radolan lonlat-coordinates")
print(u"      {0}  {1} ".format('lon [degE]', 'lat [degN]'))
print("ll: {:10.4f}  {:10.4f} ".format(lon_wgs0[0, 0], lat_wgs0[0, 0]))
print("lr: {:10.4f}  {:10.4f} ".format(lon_wgs0[0, -1], lat_wgs0[0, -1]))
print("ur: {:10.4f}  {:10.4f} ".format(lon_wgs0[-1, -1], lat_wgs0[-1, -1]))
print("ul: {:10.4f}  {:10.4f} ".format(lon_wgs0[-1, 0], lat_wgs0[-1, 0]))
print("\n-----------------------------------")
print("transformed radolan gk3-coordinates")
print(u"     {0}   {1} ".format('easting [m]', 'northing [m]'))
print("ll: {:10.0f}   {:10.0f} ".format(x_gk3[0, 0], y_gk3[0, 0]))
print("lr: {:10.0f}   {:10.0f} ".format(x_gk3[0, -1], y_gk3[0, -1]))
print("ur: {:10.0f}   {:10.0f} ".format(x_gk3[-1, -1], y_gk3[-1, -1]))
print("ul: {:10.0f}   {:10.0f} ".format(x_gk3[-1, 0], y_gk3[-1, 0]))

