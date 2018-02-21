
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # API-Change 

# This notebook shows $\omega radlib's$ ability to warn the user of pending changes in the api. Function-`@decorators` are used for this. With the `@deprecated`-decorator a `DeprecationWarning` is issued, while the `@apichange_kwarg`-decorator issues `DeprecationWarning` about changes in the calling parameters. Besides warning the new behaviour can already be utilized by a given transformation function.

# In[ ]:


# import section
import sys
import warnings
#warnings.filterwarnings('ignore')
import numpy as np
import matplotlib.pyplot as pl
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()

with warnings.catch_warnings():
    warnings.filterwarnings("always",category=DeprecationWarning)
    import wradlib as wrl


# ## Deprecation Warning

# In[ ]:


@wrl.util.deprecated()
def old_function(z):
    return z


# In[ ]:


old_function(1)


# In[ ]:


def new_function(x):
    return 0


# In[ ]:


@wrl.util.deprecated(new_function)
def old_function(z):
    return z


# In[ ]:


old_function(1)


# ## Future Change

# First, we define the function, where the api will be changed. The function takes parameter ``z`` and keyword argument ``x``, which excepts type `str` and defaults to none.
# 
# The new behaviour is to accept only ``int``. We define our function decorator as:
# 
# ```python
# @wrl.util.apichange_kwarg("0.6.0", par='x', typ=str, msg="x will take int data in the future")
# ```
# 
# This means that the api-change takes place from version ``0.6.0`` on, it affects parameter ``x``, which is of type ``str`` and it will display the message "x will take int data in the future".

# In[ ]:


@wrl.util.apichange_kwarg("0.6.0", par='x', typ=str, msg="x will take int data in the future")
def futurechange(z, x=None):
    if isinstance(x, str):
        print(z, x, type(x),
              "normal function behaviour, DeprecationWarning is issued")
    elif isinstance(x, type(None)):
        print(z, x, type(x),
              "normal function behaviour, no DeprecationWarning")
    else:
        print(z, x, type(x),
              "using wrong type here, no DeprecationWarning, "
              "but TypeError will be raised")
        raise TypeError("Wrong Input %s, 'str' expected" % type(x))
    sys.stdout.flush()
    return z, x


# In[ ]:


futurechange(0)


# In[ ]:


futurechange(1, x='10')


# In[ ]:


try:
    futurechange(2, x=20)
except TypeError as e:
    print("Type error: {0}".format(e))


# ## Type Changed

# When the API has changed finally, we just adapt the ``@decorator`` and we need to define a transformation function for the keyword parameter:

# In[ ]:


def help_function(x):
    return int(x)


# In[ ]:


@wrl.util.apichange_kwarg("0.6.0", par='x', typ=str, exfunc=help_function)
def typechanged(z, x=None):
    if isinstance(x, int):
        print(z, x, type(x), "normal function behaviour or type change, "
                             "DeprecationWarning is issued when 'x' "
                             "is type(str)")
    elif isinstance(x, type(None)):
        print(z, x, type(x),
              "normal function behaviour, no DeprecationWarning")
    else:
        print(z, x, type(x),
              "using wrong type here, TypeError will be raised")
        raise TypeError("Wrong Input %s, 'int' expected" % type(x))
    sys.stdout.flush()
    return z, x


# In[ ]:


typechanged(0)


# In[ ]:


typechanged(3, x='30')


# In[ ]:


typechanged(4, x=40)


# ## Name Changed

# If the name of the keyword argument has already changed, here from `x` to `y`.

# In[ ]:


@wrl.util.apichange_kwarg("0.6.0", par='x', typ=str, expar='y')
def namechanged(z, y=None):
    if isinstance(y, str):
        print(z, y, type(y), "DeprecationWarning")
    elif isinstance(y, type(None)):
        print(z, y, type(y),
              "normal function behaviour, no DeprecationWarning")
    else:
        print(z, y, type(y), "using wrong type here, TypeError is issued")
        raise TypeError("Wrong Input %s, 'str' expected" % type(y))
    sys.stdout.flush()
    return z, y


# In[ ]:


namechanged(0)


# In[ ]:


namechanged(5, x='50')


# In[ ]:


try:
    namechanged(6, x=60)
except TypeError as e:
    print("Type error: {0}".format(e))


# In[ ]:


namechanged(7, y='70')


# In[ ]:


try:
    namechanged(8, y=80)
except TypeError as e:
    print("Type error: {0}".format(e))


# ## Name and Type changed

# In[ ]:


@wrl.util.apichange_kwarg("0.6.0", par='x', typ=str, expar='y',
                          exfunc=help_function)
def name_and_type_changed(z, y=None):
    if isinstance(y, int):
        print(z, y, type(y),
              "normal function behaviour or paramter and type change, "
              "DeprecationWarning is issued when 'x' is given")
    elif isinstance(y, type(None)):
        print(z, y, type(y),
              "normal function behaviour, no DeprecationWarning")
    else:
        print(z, y, type(y),
              "using wrong type here, TypeError will be raised")
        raise TypeError("Wrong Input %s, 'str' expected" % type(y))
    return z, y


# In[ ]:


name_and_type_changed(0)


# In[ ]:


name_and_type_changed(9, x='90')


# In[ ]:


try:
    name_and_type_changed(10, x=100)
except TypeError as e:
    print("Type error: {0}".format(e))

