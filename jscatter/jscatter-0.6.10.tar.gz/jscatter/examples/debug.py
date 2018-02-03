# -*- coding: utf-8 -*-
#  this file is intended to used in the debugger
# write a script that calls your function to debug it

import jscatter as js
import numpy as np
import sys
# some arrays
w=np.r_[-100:100]
q=np.r_[0:10:0.1]
x=np.r_[1:10]

p=js.grace()



p.plot(x,2*x,symbol=[1],li=[1,1,1,1])


