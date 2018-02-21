
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # Clutter detection using the Gabella approach

# In[ ]:


import matplotlib.pyplot as pl
import numpy as np
import wradlib.vis as vis
import wradlib.clutter as clutter
import wradlib.util as util
import warnings
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()
import numpy as np


# ### Read the data

# In[ ]:


filename = util.get_wradlib_data_file('misc/polar_dBZ_fbg.gz')
data = np.loadtxt(filename)


# ### Apply filter

# In[ ]:


clmap = clutter.filter_gabella(data,
                               wsize=5,
                               thrsnorain=0.,
                               tr1=6.,
                               n_p=8,
                               tr2=1.3)


# ### Plot results

# In[ ]:


fig = pl.figure(figsize=(12,8))
ax = fig.add_subplot(121)
ax, pm = vis.plot_ppi(data, ax=ax)
ax.set_title('Reflectivity')
ax = fig.add_subplot(122)
ax, pm = vis.plot_ppi(clmap, ax=ax)
ax.set_title('Cluttermap')

