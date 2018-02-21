
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # A one hour tour of wradlib
# 
# ![caption](files/cover_image.png)

# This notebook provides a guided tour of some $\omega radlib$ notebooks. 

# *(find all wradlib notebooks in the [docs](http://wradlib.org/wradlib-docs/latest/notebooks.html).)*

# ## Some background, first

# Development started in 2011...or more precisely:
# 
# `October 26th, 2011`

# ### Key motivation
# 
# `A community platform for collaborative development of algorithms`

# ## Development team

# ### Core team (in aphabetical order)
# 
# - Maik Heistermann (University of Potsdam)
# - Kai Muehlbauer (University of Bonn)
# - *Thomas Pfaff (retired from radar science)*

# ### Contributions from
# 
# - Irene Crisologo (University of Potsdam, Germany)
# - Edouard Goudenhooft (RMI, Belgium)
# - Stephan Jacobi (University of Potsdam, Germany)
# - Jonathan J. Helmus (Argonne National Laboratory, USA)
# - Scott Sinclair (University of Kwazulu-Natal, South Africa)
# - ...

# ## Your entry points

# ### Just start out from [wradlib.org](http://wradlib.org)

# ### Documentation
# 
# Check out the [online docs](http://wradlib.org/wradlib-docs/latest/) with [tutorials and examples](http://wradlib.org/wradlib-docs/latest/notebooks.html) and a comprehensive [library reference](http://wradlib.org/wradlib-docs/latest/reference.html)

# ### User group
# 
# Get help and connect more than 120 users at the [wradlib user group](https://groups.google.com/forum/?fromgroups#!forum/wradlib-users)!

# ### For developers
# 
# Fork us from https://github.com/wradlib/wradlib or [raise an issue](https://github.com/wradlib/wradlib/issues)!

# ## Installation

# The are many ways to install wradlib, but this is our recommendation:

# ### 1. Install Anaconda
# 
# Get it [here](https://www.continuum.io/why-anaconda/) for Windows, Linux, or Mac.

# ### 2. Create a fresh environment and add conda-forge channel
# 
# ```bash
# $ conda create --name wradlibenv python=2.7
# $ conda config --add channels conda-forge
# ```

# ### 3. Activate environment and install wradlib
# 
# ```bash
# $ activate wradlibenv
# $ (wradlibenv) conda install wradlib
# ```

# ### 4. Make sure `GDAL_DATA` is set
# 
# The environment variable `GDAL_DATA` should point to `.../anaconda/envs/wradlibenv/share/gdal`

# ## Download the sample data

# ### 1. Download the sample data
# 
# Download the data from [here](https://github.com/wradlib/wradlib-data) either as a ziip archive or by `git clone https://github.com/wradlib/wradlib-data` 

# ### 2. Set the environment variable `WRADLIB_DATA`
# 
# `WRADLIB_DATA` should point to the upper level `wradlib-data` directory in which you saved the data. 

# Get more detailed instructions [here](http://wradlib.org/wradlib-docs/latest/gettingstarted.html)!

# ## Development paradigm

# ### Keep the magic to a minimum

# - transparent 
# - flexible
# - but also lower level

# ### Flat (or no) data model

# - pass data as numpy arrays,
# - and pass metadata as dictionaries.

# ## Import wradlib

# In[ ]:


import wradlib


# In[ ]:


# check installed version
print(wradlib.__version__)


# In the next cell, type `wradlib.` and hit `Tab`.
# 
# *Inpect the available modules and functions.*

# ## Reading and viewing data 

# ### Read and quick-view
# Let's see how we can [read and quick-view a radar scan](visualisation/wradlib_plot_ppi_example.ipynb).

# ### Zoo of file formats
# This notebook shows you how to [access various file formats](fileio/wradlib_radar_formats.ipynb).

# ## Addressing errors

# ### Attenuation
# 
# In [this example](attenuation/wradlib_attenuation.ipynb), we reconstruct path-integrated attenuation from single-pol data of the German Weather Service. 

# ### Clutter detection
# 
# wradlib provides several methods for clutter detection. [Here](classify/wradlib_fuzzy_echo_classify.ipynb), we look at an example that uses dual-pol moments and a simple fuzzy classification.

# ### Partial beam blockage
# 
# In [this example](beamblockage/wradlib_beamblock.ipynb), wradlib attempts to quantify terrain-induced beam blockage from a DEM.

# ## Integration with other geodata

# ### Average precipitation over your river catchment
# 
# In this example, we [compute zonal statistics](zonalstats/wradlib_zonalstats_quickstart.ipynb) over polygons imported in a shapefile.

# ### Over and underlay of other geodata
# 
# Often, you need to [present your radar data in context with other geodata](visualisation/wradlib_overlay.ipynb) (DEM, rivers, gauges, catchments, ...).

# ## Merging with other sensors

# ### Adjusting radar-based rainfall estimates by rain gauges
# 
# In [this example](multisensor/wradlib_adjust_example.ipynb), we use synthetic radar and rain gauge observations and confront them with different adjustment techniques.
