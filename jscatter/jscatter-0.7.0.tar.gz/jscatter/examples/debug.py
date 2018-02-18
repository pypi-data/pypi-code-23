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



R=3;NN=20;nFib=50
grid= np.mgrid[-2*R:2*R:1j*2*NN, -2*R:2*R:1j*2*NN,-2*R:2*R:1j*2*NN].reshape(3,-1).T
# points inside of sphere with radius R
p=1;p2=1*2 # p defines a superball with 1->sphere p=inf cuboid ....
inside=lambda xyz,R0,R1,R2:(np.abs(xyz[:,0])/R0)**p2+(np.abs(xyz[:,1])/R1)**p2+(np.abs(xyz[:,2])/R2)**p2<=1
insidegrid=grid[inside(grid,R,R,1.5*R)]
q=np.r_[0:5:0.1]
p=js.grace()
p.title('compare formfactors of a sphere')
ffe=js.ff.cloudScattering(q,insidegrid,rms=0.01)    # takes about 1.9 s on single core
p.plot(ffe,legend='cloud ff explicit')

ffe=js.ff.cloudScattering(q,insidegrid,formfactor='sphere',V=1,rms=0.01,ffpolydispersity=0.1)    # takes about 1.9 s on single core
p.plot(ffe,legend='cloud ff explicit')


ffa=js.ff.ellipsoid(q,1.5*R,R,beta=True)
p.plot(ffa.X,ffa.Y/ffa.I0,li=1,sy=0,legend='analytic formula')
p.yaxis(scale='l')


