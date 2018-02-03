import jscatter as js
import numpy as np

# Basic fit examples with synthetic data. Usually data are loaded from a file.

# Fit sine to simulated data
x=np.r_[0:10:0.1]
data=js.dA(np.c_[x,np.sin(x)+0.2*np.random.randn(len(x)),x*0+0.2].T)           # simulate data with error
data.fit(lambda x,A,a,B:A*np.sin(a*x)+B,{'A':1.2,'a':1.2,'B':0},{},{'x':'X'})  # fit data
data.showlastErrPlot()                                                         # show fit
data.errPlotTitle('Fit Sine')

# Fit sine to simulated data using an attribute in data with same name
data=js.dA(np.c_[x,1.234*np.sin(x)+0.1*np.random.randn(len(x)),x*0+0.1].T)     # create data
data.A=1.234                                                                   # add attribute
data.makeErrPlot()                                                             # makes erroplot prior to fit
data.fit(lambda x,A,a,B:A*np.sin(a*x)+B,{'a':1.2,'B':0},{},{'x':'X'})          # fit using .A
data.errPlotTitle('Fit Sine with attribute')

# Fit sine to simulated data using an attribute in data with different name and fixed B
data=js.dA(np.c_[x,1.234*np.sin(x)+0.1*np.random.randn(len(x)),x*0+0.1].T)       # create data
data.dd=1.234                                                                    # add attribute
data.fit(lambda x,A,a,B:A*np.sin(a*x)+B,{'a':1.2,},{'B':0},{'x':'X','A':'dd'})   # fit data
data.showlastErrPlot()                                                           # show fit
data.errPlotTitle('Fit Sine with attribut and fixed B')

# Fit sine to simulated dataList using an attribute in data with different name and fixed B from data.
# first one common parameter then as parameter list
data=js.dL()
ef=0.1  # increase this to increase error bars of final result
for ff in [0.001,0.4,0.8,1.2,1.6]:                                                      # create data
   data.append( js.dA(np.c_[x,(1.234+ff)*np.sin(x+ff)+ef*ff*np.random.randn(len(x)),x*0+ef*ff].T) )
   data[-1].B=0.2*ff/2                                                                 # add attributes
# fit with a single parameter for all data, obviously wrong result
data.fit(lambda x,A,a,B,p:A*np.sin(a*x+p)+B,{'a':1.2,'p':0,'A':1.2},{},{'x':'X'})
data.showlastErrPlot()                                                                 # show fit
data.errPlotTitle('Fit Sine with attribut and common fit parameter')
# now allowing multiple p,A,B as indicated by the list starting value
data.fit(lambda x,A,a,B,p:A*np.sin(a*x+p)+B,{'a':1.2,'p':[0],'B':[0,0.1],'A':[1]},{},{'x':'X'})
data.errPlotTitle('Fit Sine with attribut and non common fit parameter')
# plot p against A , just as demonstration
p=js.grace()
p.plot(data.A,data.p,data.p_err)


# 3D fit data with an X,Z grid data and Y values
# For 3D fit we calc Y values from X,Z coordinates (only for scalar Y data).
# For fitting we need data in X,Z,Y column format.
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
#
# create 3D data with X,Z axes and Y values as Y=f(X,Z)
x,z=np.mgrid[-5:5:0.25,-5:5:0.25]
xyz=js.dA(np.c_[x.flatten(),z.flatten(),0.3*np.sin(x*z/np.pi).flatten()+0.01*np.random.randn(len(x.flatten())),0.01*np.ones_like(x).flatten() ].T)
# set columns where to find X,Y,Z )
xyz.setColumnIndex(ix=0,iz=1,iy=2,iey=3)
#
ff=lambda x,z,a,b:a*np.sin(b*x*z)
xyz.fit(ff,{'a':1,'b':1/3.},{},{'x':'X','z':'Z'})
#
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_title('3D Sinusoidal fit')
ax.scatter(xyz.X,xyz.Z,xyz.Y)
ax.tricontour(xyz.lastfit.X,xyz.lastfit.Z,xyz.lastfit.Y, cmap=cm.coolwarm,linewidth=0, antialiased=False)
plt.show(block=False)
