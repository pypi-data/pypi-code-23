
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # Reading NetCDF files with a generic reader
# 
# In this example, we read NetCDF files from different sources using a generic reader from $\omega radlib's$ io module.

# In[ ]:


from wradlib.io import read_generic_netcdf
from wradlib.util import get_wradlib_data_file
import os


# In[ ]:


# A little helper function for repeated tasks
def read_and_overview(filename):
    """Read NetCDF using read_generic_netcdf and print upper level dictionary keys
    """
    test = read_generic_netcdf(filename)
    print("\nPrint keys for file %s" % os.path.basename(filename))
    for key in test.keys():
        print("\t%s" % key)


# ### CfRadial example from TITAN homepage
# 
# See also: http://www.ral.ucar.edu/projects/titan/docs/radial_formats

# In[ ]:


filename = 'netcdf/cfrad.20080604_002217_000_SPOL_v36_SUR.nc'
filename = get_wradlib_data_file(filename)
read_and_overview(filename)


# ### Example PPI from Py-ART repository
# 
# See also: https://github.com/ARM-DOE/pyart/

# In[ ]:


filename = 'netcdf/example_cfradial_ppi.nc'
filename = get_wradlib_data_file(filename)
read_and_overview(filename)


# ### Example RHI from Py-ART repository
# See also: https://github.com/ARM-DOE/pyart/

# In[ ]:


filename = 'netcdf/example_cfradial_rhi.nc'
filename = get_wradlib_data_file(filename)
read_and_overview(filename)


# ### Example EDGE NetCDF export format

# In[ ]:


filename = 'netcdf/edge_netcdf.nc'
filename = get_wradlib_data_file(filename)
read_and_overview(filename)

