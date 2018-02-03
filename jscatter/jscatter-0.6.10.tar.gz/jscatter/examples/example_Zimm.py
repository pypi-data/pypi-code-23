import numpy as np

import jscatter as js

x=js.loglist(0.02,40,100)#np.r_[0.02:0.3:0.02,0.3:3:0.2,3:40:1]
qmax=2;step=0.15

pp=js.grace()
pp.multi(1,2)
p0=pp[0];p1=pp[1]
showinternal=0

# example to show finiteZimm dynamics
if 0:
    p1.title('contributions to overall Rouse dynamics',size=1)
    p0.title('modecontribution factors',size=1)
    #zz1=js.formel.fqtfiniteRouse(x,np.r_[0.1:qmax:step],124,7,ll=0.38,Dcm=.3,tintern=0.,Temp=273+60)
    x*=100
    zz1=js.dynamic.finiteRouse(x,np.r_[0.1:qmax:step],100,[0]*20+[1]*20,ll=11.7/100**0.5,Wl4=9234e-4,tintern=0.,Temp=273+60)
    for i,z in enumerate(zz1,1):
        p1.plot(z.X,z.Y,line=[1,1,i],symbol=0,legend='q=%g'%z.q)
        p1.plot(z.X,z[2],line=[3,2,i],symbol=0,legend='q=%g diff'%z.q)
    
    for i,mc in enumerate(np.array(zz1.modecontribution).T,1):
        p0.plot(zz1.q,mc,li=[1,2,i],sy=0,legend='mode %i' %i)
    
    p1.yaxis(min=0.0,max=1.0,scale='n')
    p1.xaxis(min=min(x),max=max(x),scale='l')
    p0.yaxis(min=0.003,max=1.2,scale='n')
    p0.xaxis(min=0.0,max=qmax,scale='n')
    p1.legend(x=3.,y=0.6,charsize=0.5)
    p0.legend(x=0.1,y=0.5,charsize=0.5)
    p1.title('contributions to overall Rouse dynamics',size=1)
    p1.subtitle('\\xt\\f{}\\sRouse\\N=%.3g ns , \\xt\\f{}\\sintern\\N=%.3g ns' %(zz1.trouse[0],zz1.tintern[0]))

    #p0.subtitle('\\xt\\f{}\\sZimm\\N=%.3g ns' %(z.tzimm))
    p0.autoscale()
else:
    p1.title('contributions to overall zimm dynamics',size=1)
    p0.title('modecontribution factors',size=1)
    zz1=js.dynamic.finiteZimm(x,np.r_[0.1:qmax:step],124,7,ll=0.38,tintern=0.,mu=0.55,Temp=273+60,viscosity=.565)
    for i,z in enumerate(zz1,1):
        p1.plot(z.X,z.Y,line=[1,1,i],symbol=0,legend='q=%g'%z.q)
        p1.plot(z.X,z[2],line=[3,2,i],symbol=0,legend='q=%g diff'%z.q)
    
    for i,mc in enumerate(np.array(zz1.modecontribution).T,1):
        p0.plot(zz1.q,mc,li=[1,2,i],sy=0,legend='mode %i' %i)
    
    p1.yaxis(min=0.03,max=1.01,scale='l')
    p1.xaxis(min=0.02,max=max(x),scale='l')
    p0.yaxis(min=0.003,max=1.2,scale='n')
    p0.xaxis(min=0.0,max=qmax,scale='n')
    p1.legend(x=9.3,y=1.0,charsize=0.5)
    p0.legend(x=0.1,y=0.5,charsize=0.5)
    p1.subtitle('\\xt\\f{}\\sZimm\\N=%.3g ns , \\xt\\f{}\\sintern\\N=%.3g ns' %(z.tzimm,z.tintern))
    #p0.subtitle('\\xt\\f{}\\sZimm\\N=%.3g ns' %(z.tzimm))
    p0.autoscale()
