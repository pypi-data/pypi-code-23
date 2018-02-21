
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # RADOLAN binary data format

# The RADOLAN binary data file format is described in the RADOLAN Kompositformat. The radolan composite files consists of an ascii header containing all needed information to decode the following binary data block. $\omega radlib$ provides [wradlib.io.read_RADOLAN_composite()](http://wradlib.org/wradlib-docs/latest/generated/wradlib.io.read_RADOLAN_composite.html) to read the data.
# 
# The function `wradlib.io.parse_DWD_quant_composite_header()` takes care of correctly decoding the ascii header. All available header information is transferred into the metadata dictionary.

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
filehandle = wrl.io.get_radolan_filehandle(rw_filename)
header = wrl.io.read_radolan_header(filehandle)
print(header)


# In[ ]:


attrs = wrl.io.parse_DWD_quant_composite_header(header)
print(attrs)


# In the following example, the header information of four different composites is extracted.

# In[ ]:


# load radolan file
filename = 'radolan/showcase/raa01-rx_10000-1408102050-dwd---bin.gz'
rx_filename = wrl.util.get_wradlib_data_file(filename)
filename = 'radolan/showcase/raa01-ex_10000-1408102050-dwd---bin.gz'
ex_filename = wrl.util.get_wradlib_data_file(filename)
filename = 'radolan/showcase/raa01-rw_10000-1408102050-dwd---bin.gz'
rw_filename = wrl.util.get_wradlib_data_file(filename)
filename = 'radolan/showcase/raa01-sf_10000-1408102050-dwd---bin.gz'
sf_filename = wrl.util.get_wradlib_data_file(filename)

rxdata, rxattrs = wrl.io.read_RADOLAN_composite(rx_filename)
exdata, exattrs = wrl.io.read_RADOLAN_composite(ex_filename)
rwdata, rwattrs = wrl.io.read_RADOLAN_composite(rw_filename)
sfdata, sfattrs = wrl.io.read_RADOLAN_composite(sf_filename)

# print the available attributes
print("RX Attributes:")
for key, value in rxattrs.items():
    print(key + ':', value)
print("----------------------------------------------------------------")
# print the available attributes
print("EX Attributes:")
for key, value in exattrs.items():
    print(key + ':', value)
print("----------------------------------------------------------------")

# print the available attributes
print("RW Attributes:")
for key, value in rwattrs.items():
    print(key + ':', value)
print("----------------------------------------------------------------")

# print the available attributes
print("SF Attributes:")
for key, value in sfattrs.items():
    print(key + ':', value)
print("----------------------------------------------------------------")

