
import jscatter as js
import numpy as np

Q=js.loglist(0.001,5,500)#np.r_[0.01:5:0.01]

ffmV=js.ff.multilamellarVesicles
save=0

# correlation peak sharpness depends on disorder
dR=20
nG=200
p=js.grace(1,1)
for dd in [0.1,6,10]:
    p.plot(ffmV(Q=Q, R=100, displace=dd, dR=dR,N=10,dN=0, phi=0.2,shellthickness=0, SLD=1e-4,nGauss=nG),le='displace= %g ' %(dd))

p.legend(x=0.3,y=10)
p.title('Scattering of multilamellar vesicle')
p.subtitle('shellnumber N=10, shellthickness 0 nm, dR=20, R=100')
p.yaxis(label='S(Q)',scale='l',min=1e-7,max=1e2,ticklabel=['power',0])
p.xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])
p.text('Guinier range',x=0.005,y=10)
p.text(r'Correlation peaks\nsharpness decreases with disorder',x=0.02,y=0.00001)
if save:p.save('multilamellar1.png')

# Correlation peak position depends on average layer distance
dd=0
dR=20
nG=200
p=js.grace(1,1)
for N in [1,3,10,30,100]:
    p.plot(ffmV(Q=Q, R=100, displace=dd, dR=dR,N=N,dN=0, phi=0.2,shellthickness=0, SLD=1e-4,nGauss=nG),le='N= %g ' %(N))

p.legend(x=0.3,y=10)
p.title('Scattering of multilamellar vesicle')
p.subtitle('shellnumber N, shellthickness 0 nm, dR=20, R=100')
p.yaxis(label='S(Q)',scale='l',min=1e-7,max=1e2,ticklabel=['power',0])
p.xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])

p.text('Guinier range',x=0.005,y=40)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R',x=0.2,y=0.01)
if save:p.save('multilamellar2.png')

# including the shell formfactor with shape fluctuations
dd=2
dR=20
nG=200
p=js.grace(1,1)
for i,ds in enumerate([0.001,0.1,0.6,1.2],1):
    mV=ffmV(Q=Q, R=100, displace=dd, dR=dR,N=10,dN=0, phi=0.2,shellthickness=6,ds=ds, SLD=1e-4,nGauss=nG)
    p.plot( mV,sy=[i,0.3,i],le='ds= %g ' %(ds))
    p.plot(mV.X,mV[-1]*1000,sy=0,li=[3,3,i])
    p.plot(mV.X,mV[-2]*100,sy=0,li=[2,3,i])

p.legend(x=0.003,y=1)
p.title('Scattering of multilamellar vesicle')
p.subtitle('shellnumber N=10, shellthickness 6 nm, dR=20, R=100')
p.yaxis(label='S(Q)',scale='l',min=1e-10,max=1e6,ticklabel=['power',0])
p.xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])

p.text('Guinier range',x=0.005,y=40000)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R',x=0.2,y=10)
p.text('Shell form factor',x=0.1,y=1e-4)
p[0].line(0.2,4e-5,0.8,4e-5,2,arrow=2)
p.text(r'Shell structure factor\n x100',x=0.002,y=5e1)
p.text('Shell form factor x1000',x=0.01,y=1e-6)
if save:p.save('multilamellar3.png')


# Comparing multilamellar and unilamellar vesicle
dd=2
dR=5
nG=100
ds=0.2
p=js.grace(1,1)
for i,R in enumerate([40,50,60],1):
    mV=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=4,dN=0, phi=0.2,shellthickness=6,ds=ds, SLD=1e-4,nGauss=nG)
    p.plot( mV,sy=[i,0.3,i],le='R= %g ' %(R))
    p.plot(mV.X,mV[-1]*100,sy=0,li=[3,3,i])
    p.plot(mV.X,mV[-2]*0.01,sy=0,li=[2,3,i])


# comparison double sphere
mV=ffmV(Q=Q, R=50., displace=0, dR=5,N=1,dN=0, phi=1,shellthickness=6,ds=ds, SLD=1e-4,nGauss=100)
p.plot(mV,sy=0,li=[1,2,4],le='unilamellar R=50 nm')
mV=ffmV(Q=Q, R=60., displace=0, dR=5,N=1,dN=0, phi=1,shellthickness=6,ds=ds, SLD=1e-4,nGauss=100)
p.plot(mV,sy=0,li=[3,2,4],le='unilamellar R=60 nm')


p.legend(x=0.3,y=1e5)
p.title('Comparing multilamellar and unilamellar vesicle')
p.subtitle('shellnumber N=4, shellthickness 6 nm, dR=5, ds=0.2')
p.yaxis(label='S(Q)',scale='l',min=1e-10,max=1e6,ticklabel=['power',0])
p.xaxis(label='Q / nm\S-1',scale='l',min=1e-2,max=5,ticklabel=['power',0])

p.text('Guinier range',x=0.05,y=40000)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R',x=0.2,y=10)
p.text('Shell form factor',x=0.2,y=1e-4)
p[0].line(0.2,4e-5,0.8,4e-5,2,arrow=2)
p.text(r'Shell structure factor\n x0.01',x=0.011,y=0.1)
p.text('Shell form factor x100',x=0.02,y=1e-6)
if save:p.save('multilamellar4.png')


# Lipid bilayer in SAXS/SANS
# Values for layer thickness can be found in
# Structure of lipid bilayers
# John F. Nagle et al Biochim Biophys Acta. 1469, 159–195. (2000)
Q=js.loglist(0.01,5,500)
dd=1.5
dR=5
nG=100
ds=0
R=50
N=5
st=[3.5,(6.5-3.5)/2]
p=js.grace(1,1)
p.title('Lipid bilayer in SAXS/SANS')
# SAXS
saxm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=N,dN=0, phi=0.2,shellthickness=st,ds=ds, SLD=[0.6e-3,0.07e-3],solventSLD=0.94e-3,nGauss=nG)
p.plot(saxm,sy=[1,0.3,1],le='SAXS multilamellar')
saxu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,shellthickness=st,ds=ds,SLD=[0.6e-3,0.07e-3],solventSLD=0.94e-3,nGauss=100)
p.plot(saxu,sy=0,li=[3,2,1],le='SAXS unilamellar')
# SANS
sanm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=N,dN=0, phi=0.2,shellthickness=st,ds=ds, SLD=[1.5e-4,0.3e-4],solventSLD=6.335e-4,nGauss=nG)
p.plot( sanm,sy=[1,0.3,2],le='SANS multilamellar')
sanu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,shellthickness=st,ds=ds,SLD=[1.5e-4,0.3e-4],solventSLD=6.335e-4,nGauss=100)
p.plot(sanu,sy=0,li=[3,2,2],le='SANS unilamellar')


p.legend(x=0.015,y=1e-1)
p.subtitle('R=50 nm, N=5, shellthickness=[1.5,3.5,1.5] nm, dR=5, ds=0.')
p.yaxis(label='S(Q)',scale='l',min=1e-6,max=1e4,ticklabel=['power',0])
p.xaxis(label='Q / nm\S-1',scale='l',min=1e-2,max=5,ticklabel=['power',0])

p.text('Guinier range',x=0.03,y=3000)
p.text(r'Correlation peak\n at 2\xp\f{}N/R\n vanishes for SAXS',x=0.5,y=4)
p.text('Shell form factor',x=0.1,y=1e-4)
if save:p.save('multilamellar5.png')

# Example for a liposome doubleLayer for SAX and SANS with ds>0
dd=1.5
dR=5
nG=100
ds=0.01
R=50
sd=[3,1]

p=js.grace()
p.title('Multilamellar/unilamellar vesicle for SAXS/SANS')
# SAXS
saxm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=4,dN=0, phi=0.2,shellthickness=sd,ds=ds, SLD=[0.6e-3,0.07e-3],solventSLD=0.94e-3,nGauss=nG)
p.plot(saxm,sy=0,li=[1,1,1],le='SAXS multilamellar')
saxu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,shellthickness=sd,ds=ds,SLD=[0.6e-3,0.07e-3],solventSLD=0.94e-3,nGauss=100)
p.plot(saxu,sy=0,li=[3,2,1],le='SAXS unilamellar')
saxu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,shellthickness=sd,ds=0,SLD=[0.6e-3,0.07e-3],solventSLD=0.94e-3,nGauss=100)
p.plot(saxu,sy=0,li=[2,0.3,1],le='SAXS unilamellar ds=0')

# SANS
sanm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=4,dN=0, phi=0.2,shellthickness=sd,ds=ds, SLD=[1.5e-4,0.3e-4],solventSLD=6.335e-4,nGauss=nG)
p.plot( sanm,sy=0,li=[1,1,2],le='SANS multilamellar')
sanu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,shellthickness=sd,ds=ds,SLD=[1.5e-4,0.3e-4],solventSLD=6.335e-4,nGauss=100)
p.plot(sanu,sy=0,li=[3,2,2],le='SANS unilamellar')
sanu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,shellthickness=sd,ds=0,SLD=[1.5e-4,0.3e-4],solventSLD=6.335e-4,nGauss=100)
p.plot(sanu,sy=0,li=[2,0.3,2],le='SANS unilamellar ds=0')

p.legend(x=0.013,y=3e-1)
p.title('Comparing multilamellar and unilamellar vesicle')
p.subtitle('R=50 nm, N=4, shellthickness=[1,3,1] nm, dR=5, ds=0.2')
p.yaxis(label='S(Q)',scale='l',min=1e-7,max=1e4,ticklabel=['power',0])
p.xaxis(label='Q / nm\S-1',scale='l',min=1e-2,max=5,ticklabel=['power',0])

p.text('Guinier range',x=0.03,y=2000)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R',x=0.3,y=10)
p.text('Shell form factor',x=0.1,y=1e-4)
p[0].line(0.2,4e-4,0.6,4e-4,2,arrow=2)
p.text('Shell form factor ds=0',x=0.1,y=1e-4)
p[0].line(0.2,4e-5,0.6,4e-5,2,arrow=2)




