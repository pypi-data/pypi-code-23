
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # Zonal Statistics

# The [wradlib.zonalstats](http://wradlib.org/wradlib-docs/latest/zonalstats.html) module provides classes and functions for calculation of zonal statistics for data on arbitrary grids and projections.
# 
# It provides classes for:
# 
# - managing georeferenced data (grid points or grid polygons, zonal polygons),
# - calculation of geographic intersections and managing resulting vector data
# - calculation of zonal statistics and managing result data as vector attributes
# - output to vector and raster files available within ogr/gdal

# In[ ]:


import wradlib as wrl
import matplotlib.pyplot as pl
import matplotlib as mpl
import warnings
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()
import numpy as np


# ## DataSource

# The [wradlib.zonalstats.DataSource](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.DataSource.html) class handles point or polygon vector data by wrapping ogr.DataSource with special functions.
# 
# The following example shows how to create different DataSource objects:

# In[ ]:


from osgeo import osr

# create gk zone 2 projection osr object
proj_gk2 = osr.SpatialReference()
proj_gk2.ImportFromEPSG(31466)

# Setting up DataSource
box0 = np.array([[2600000., 5630000.],[2600000., 5640000.],
                 [2610000., 5640000.],[2610000., 5630000.],
                 [2600000., 5630000.]])
box1 = np.array([[2610000., 5630000.],[2610000., 5640000.],
                 [2620000., 5640000.],[2620000., 5630000.],
                 [2610000., 5630000.]])
box2 = np.array([[2600000., 5640000.],[2600000., 5650000.],
                 [2610000., 5650000.],[2610000., 5640000.],
                 [2600000., 5640000.]])
box3 = np.array([[2610000., 5640000.],[2610000., 5650000.],
                 [2620000., 5650000.],[2620000., 5640000.],
                 [2610000., 5640000.]])

point0 = np.array(wrl.georef.get_centroid(box0))
point1 = np.array(wrl.georef.get_centroid(box1))
point2 = np.array(wrl.georef.get_centroid(box2))
point3 = np.array(wrl.georef.get_centroid(box3))

# creates Polygons in Datasource
poly = wrl.zonalstats.DataSource(np.array([box0, box1, box2, box3]), srs=proj_gk2, name='poly')

# creates Points in Datasource
point = wrl.zonalstats.DataSource(np.vstack((point0, point1, point2, point3)),
                                  srs=proj_gk2, name='point')


# Let's have a look at the data, which will be exported as numpy arrays. The property ``data`` exports all available data:

# In[ ]:


print(poly.data)
print(point.data)


# Currently data can also be retrieved by:
# 
# - index - [wradlib.zonalstats.DataSource.get_data_by_idx()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.DataSource.get_data_by_idx.html),
# - attribute - [wradlib.zonalstats.DataSource.get_data_by_att()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.DataSource.get_data_by_att.html) and
# - geometry - [wradlib.zonalstats.DataSource.get_data_by_geom()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.DataSource.get_data_by_geom.html).

# Now, with the DataSource being created, we can add/set attribute data of the features:

# In[ ]:


# add attribute
poly.set_attribute('mean', np.array([10.1, 20.2, 30.3, 40.4]))
point.set_attribute('mean', np.array([10.1, 20.2, 30.3, 40.4]))


# Attributes associated with features can also be retrieved:

# In[ ]:


# get attributes
print(poly.get_attributes(['mean']))
# get attributes filtered
print(poly.get_attributes(['mean'], filt=('index', 2)))


# Finally, we can export the contained data to OGR/GDAL supported [vector](http://www.gdal.org/ogr_formats.html) and [raster](http://www.gdal.org/formats_list.html) files:

# In[ ]:


# dump as 'ESRI Shapefile', default
poly.dump_vector('test_poly.shp')
point.dump_vector('test_point.shp')
# dump as 'GeoJSON'
poly.dump_vector('test_poly.geojson', 'GeoJSON')
point.dump_vector('test_point.geojson', 'GeoJSON')
# dump as 'GTiff', default
poly.dump_raster('test_poly_raster.tif', attr='mean', pixel_size=100.)
# dump as 'netCDF'
poly.dump_raster('test_poly_raster.nc', 'netCDF', attr='mean', pixel_size=100.)


# ## ZonalData

# ZonalData is usually available as georeferenced regular gridded data. Here the [wradlib.zonalstats.ZonalDataBase](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.ZonalDataBase.html) class manages the grid data, the zonal data (target polygons) and the intersection data of source grid and target polygons.
# Because the calculation of intersection is different for point grids and polygon grids, we have subclasses [wradlib.zonalstats.ZonalDataPoly](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.ZonalDataPoly.html) and [wradlib.zonalstats.ZonalDataPoint](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.ZonalDataPoint.html).
# 
# Basically, [wradlib.zonalstats.ZonalDataBase](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.ZonalDataBase.html) encapsulates three [wradlib.zonalstats.DataSource](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.DataSource.html) objects:
# 
# - source grid (points/polygons)
# - target polygons
# - destination (intersection) (points/polygons)
# 
# The destination DataSource object is created from the provided source grid and target polygons at initialisation time.

# As an example the creation of a [wradlib.zonalstats.ZonalDataPoly](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.ZonalDataPoly.html) class instance is shown:

# In[ ]:


# setup test grid and catchment
lon = 7.071664
lat = 50.730521
r = np.array(range(50, 100*1000 + 50 , 100))
a = np.array(range(0, 90, 1))
rays = a.shape[0]
bins = r.shape[0]
# create polar grid polygon vertices in lat,lon
radar_ll = wrl.georef.polar2polyvert(r, a, (lon, lat))

# setup OSR objects
proj_gk = osr.SpatialReference()
proj_gk.ImportFromEPSG(31466)
proj_ll = osr.SpatialReference()
proj_ll.ImportFromEPSG(4326)

# project ll grids to GK2
radar_gk = wrl.georef.reproject(radar_ll, projection_source=proj_ll,
                            projection_target=proj_gk)

# reshape
radar_gk.shape = (rays * bins, 5, 2)

box0 = np.array([[2600000., 5630000.],[2600000., 5640000.],
                 [2610000., 5640000.],[2610000., 5630000.],
                 [2600000., 5630000.]])

box1 = np.array([[2610000., 5630000.],[2610000., 5640000.],
                 [2620000., 5640000.],[2620000., 5630000.],
                 [2610000., 5630000.]])

targets = np.array([box0, box1])

zdpoly = wrl.zonalstats.ZonalDataPoly(radar_gk, targets, srs=proj_gk)


# When calculationg the intersection, also weights are calculated for every source grid feature and attributed to the destination features.
# 
# With the property ``isecs`` it is possible to retrieve the intersection geometries as numpy array, further get-functions add to the functionality:

# In[ ]:


# get intersections as numpy array
isecs = zdpoly.isecs
# get intersections for target polygon 0
isec0 = zdpoly.get_isec(0)
# get source indices referring to target polygon 0
ind0 = zdpoly.get_source_index(0)

print(isecs.shape, isec0.shape, ind0.shape)


# There are import/export functions using [ESRI-Shapfile Format](https://de.wikipedia.org/wiki/Shapefile) as data format. Next export and import is shown:
# [wradlib.zonalstats.ZonalDataBase](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.ZonalDataBase.html)

# In[ ]:


zdpoly.dump_vector('test_zdpoly')
zdpoly_new = wrl.zonalstats.ZonalDataPoly('test_zdpoly')


# ## ZonalStats

# For ZonalStats the [wradlib.zonalstats.ZonalStatsBase](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.ZonalStatsBase.html) class and the two subclasses [wradlib.zonalstats.GridCellsToPoly](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.GridCellsToPoly.html) and [wradlib.zonalstats.GridPointsToPoly](http://wradlib.org/wradlib-docs/latest/generated/wradlib.zonalstats.GridPointsToPoly.html) are available. ZonalStatsBase encapsulates one ZonalData object. Properties for simple access of ZonalData, intersection indices and weights are provided. The following code will add ``mean`` and ``var`` attributes to the target DataSource:

# In[ ]:


# create GridCellsToPoly instance
gc = wrl.zonalstats.GridCellsToPoly(zdpoly_new)
# create some artificial data for processing using the features indices
count = radar_gk.shape[0]
data = 1000000. / np.array(range(count))
# calculate mean and variance
mean = gc.mean(data)
var = gc.var(data)

print("Average:", mean)
print("Variance:", var)


# Next we can export the resulting zonal statistics to vector and raster files:

# In[ ]:


# export to vector GeoJSON
gc.zdata.trg.dump_vector('test_zonal_json.geojson', 'GeoJSON')
# export 'mean' to raster netCDF
gc.zdata.trg.dump_raster('test_zonal_hdr.nc', 'netCDF', 'mean', pixel_size=100.)


# The ZonalStats classes can also be used without any ZonalData by instantiating with precalculated index and weight values. Be sure to use matching ix, w and data arrays:

# In[ ]:


# get ix, and weight arrays
ix = gc.ix
w = gc.w
# instantiate new ZonlaStats object
gc1 = wrl.zonalstats.GridCellsToPoly(ix=ix, w=w)
# caclulate statistics
avg = gc1.mean(data)
var = gc1.var(data)

print("Average:", avg)
print("Variance:", var)


# ## Examples

# Examples of using Zonal Statistics working with rectangular grids as well as polar grids is shown in the [Zonal Statistics Example](wradlib_zonalstats_example.ipynb) notebook.
