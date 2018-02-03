# -*- coding: utf-8 -*-
# A model for protein incoherent scattering
# neglecting coherent and maybe some other contributions

import jscatter as js
import numpy as np
import urllib

# get pdb structure file with 3rn3 atom coordinates and filter for CA positions in A
# this results in C-alpha representation of protein Ribonuclease A.
url='https://files.rcsb.org/download/3RN3.pdb'
try:
    pdbtxt=urllib.urlopen(url).read()
except:
    # python3
    pdbtxt=urllib.request.urlopen(url).read().decode('utf8')
CA=[line[31:55].split() for line in pdbtxt.split('\n') if line[13:16].rstrip()=='CA' and line[:4]=='ATOM']
# conversion to nm and center of mass
ca=np.array(CA,float)/10.
cloud=ca-ca.mean(axis=0)
Dtrans=0.086  # nm**2/ns  for 3rn3 in D2O at 20°C
Drot  =0.0163 # 1/ns

# A list of wavevectors and frequencies and a resolution.
# If bgr is zero we have to add it later after the convolution with resolution as constant instrument background.
# As resolution a single q independent (unrealistic) Gaussian is used.
ql = np.r_[0.1,0.5, 1, 2:15.:2,20]
w = np.r_[-100:100:0.1]
start={'s0':0.5,'m0':0,'a0':1,'bgr':0.00}
resolution=lambda w:js.dynamic.resolution_w(w=w, **start)
res=resolution(w)

# translational diffusion
p=js.grace(3,0.75)
p.multi(1,4)
p[0].title(' '*50+'Inelastic neutron scattering for protein Ribonuclease A',size=2)
iqwRtr=js.dL([js.dynamic.convolve(js.dynamic.transDiff_w(w,q=q,D=Dtrans), res,normB=True) for q in ql])
p[0].plot(iqwRtr,le='$wavevector')
iqwRt=js.dL([js.dynamic.transDiff_w(w,q=q,D=Dtrans) for q in ql])
p[0].plot(iqwRt,li=1,sy=0)
p[0].yaxis(min=1e-8,max=1e3,scale='l',ticklabel=['power',0,1],label=[r'I(Q,\xw\f{})',1.5])
p[0].xaxis(min=-149,max=99,label=r'\xw\f{} / 1/ns',charsize=1)
p[0].legend(charsize=1,x=-140,y=1)
p[0].text(r'translational diffusion',y=80,x=-130,charsize=1.5)

# rotational diffusion
iqwRrr=js.dL([js.dynamic.convolve(js.dynamic.rotDiffusion_w(w,q=q,cloud=cloud,Dr=Drot), res,normB=True) for q in ql])
p[1].plot(iqwRrr,le='$wavevector')
iqwRr=js.dL([js.dynamic.rotDiffusion_w(w,q=q,cloud=cloud,Dr=Drot) for q in ql])
p[1].plot(iqwRr,li=1,sy=0)
p[1].yaxis(min=1e-8,max=1e3,scale='l',ticklabel=['power',0,1,'normal'])
p[1].xaxis(min=-149,max=99,label=r'\xw\f{} / 1/ns',charsize=1)
#p[1].legend()
p[1].text(r'rotational diffusion',y=50,x=-130,charsize=1.5)

# restricted diffusion
iqwRgr=js.dL([js.dynamic.convolve(js.dynamic.diffusionHarmonicPotential_w(w, q=q, tau=0.15, rmsd=0.3), res, normB=True) for q in ql])
p[2].plot(iqwRgr,le='$wavevector')
iqwRg=js.dL([js.dynamic.diffusionHarmonicPotential_w(w, q=q, tau=0.15, rmsd=0.3) for q in ql])
p[2].plot(iqwRg,li=1,sy=0)
p[2].yaxis(min=1e-8,max=1e3,scale='l',ticklabel=['power',0,1],label='')
p[2].xaxis(min=-149,max=99,label=r'\xw\f{} / 1/ns',charsize=1)
#p[2].legend()
p[2].text(r'restricted diffusion \n(harmonic)',y=50,x=-130,charsize=1.5)

# amplitudes at w=0 and w=10
p[3].title('amplitudes w=[0, 10]')
p[3].subtitle(r'\xw\f{}>10 restricted diffusion > translational diffusion')
ww=10
wi=np.abs(w-ww).argmin()
p[3].plot(iqwRtr.wavevector,iqwRtr.Y.array.max(axis=1),sy=[1,0.3,1],li=[1,2,1],le='trans + res')
p[3].plot(iqwRt.wavevector,iqwRt.Y.array.max(axis=1)  ,sy=[1,0.3,1],li=[2,2,1],le='trans ')
p[3].plot(iqwRt.wavevector,iqwRt.Y.array[:,wi]  ,sy=[2,0.3,1],li=[3,3,1],le='trans w=%.2g' %ww)
p[3].plot(iqwRrr.wavevector,iqwRrr.Y.array.max(axis=1),sy=[1,0.3,2],li=[1,2,2],le='rot + res')
p[3].plot(iqwRr.wavevector,iqwRr.Y.array.max(axis=1)  ,sy=[1,0.3,2],li=[2,2,2],le='rot')
p[3].plot(iqwRr.wavevector,iqwRr.Y.array[:,wi]  ,sy=[2,0.3,2],li=[3,3,2],le='rot w=%.2g' %ww)
p[3].plot(iqwRgr.wavevector,iqwRgr.Y.array.max(axis=1),sy=[1,0.3,3],li=[1,2,3],le='rest + res')
p[3].plot(iqwRg.wavevector,iqwRg.Y.array.max(axis=1)  ,sy=[8,0.3,1],li=[2,2,3],le='rest')
p[3].plot(iqwRg.wavevector,iqwRg.Y.array[:,wi]  ,sy=[3,0.3,3],li=[3,3,3],le='rest w=%.2g' %ww)

p[3].yaxis(min=1e-6,max=1e3,scale='l',ticklabel=['power',0,1,'opposite'],label=[r'I(Q,\xw\f{}=[0,10])',1,'opposite'])
p[3].xaxis(min=0.1,max=50,scale='l',label='Q / nm\S-1',charsize=1)
p[3].legend(charsize=1.,x=5,y=1e-3)

# p.save('inelasticNeutronScattering.png',size=(2400,600),dpi=200)

# all together in a combined model  ----------------------------
conv=js.dynamic.convolve
start={'s0':0.5,'m0':0,'a0':1,'bgr':0.00}
resolution=lambda w:js.dynamic.resolution_w(w=w, **start)
def transrotsurfModel(w,q,Dt,Dr,exR,tau,rmsd):
    """
    A model for trans/rot diffusion with a partial local restricted diffusion at the protein surface.

    See Fast internal dynamics in alcohol dehydrogenase The Journal of Chemical Physics 143, 075101 (2015);
    https://doi.org/10.1063/1.4928512

    Parameters
    ----------
    w   frequncies
    q   wavevector
    Dt  tranlational diffusion
    Dr  rotational diffusion
    exR outside this radius additional restricted diffusion with t0 u0
    tau  correlation time
    rmsd  Root mean square displacement Ds=u0**2/t0

    Returns
    -------

    """
    natoms=cloud.shape[0]
    trans=js.dynamic.transDiff_w(w, q, Dt)
    rot=js.dynamic.rotDiffusion_w(w,q,cloud,Dr)
    fsurf=((cloud**2).sum(axis=1)**0.5>exR).sum()*1./natoms # fraction close to surface
    loc=js.dynamic.diffusionHarmonicPotential_w(w, q, tau, rmsd)
    # only a fraction at surface contributes to local restricted diffusion
    loc.Y=js.dynamic.elastic_w(w).Y*(1-fsurf)+fsurf*loc.Y
    final=conv(trans,rot)
    final=conv(final, loc)
    final.setattr(rot,'rot_')
    final.setattr(loc,'loc_')
    res=resolution(w)
    finalres=conv(final, res,normB=True)
    #finalres.Y+=0.0073
    finalres.q=q
    finalres.fsurf=fsurf
    return finalres

ql = np.r_[0.1,0.5, 1, 2:15.:4,20]
p=js.grace(1,1)
p.title('Protein incoherent scattering')
p.subtitle('Ribonuclease A')
iqwR=js.dL([transrotsurfModel(w, q=q, Dt=Dtrans, Dr=Drot, exR=0, tau=0.15, rmsd=0.3) for q in ql])
p.plot(iqwR[0],sy=0,li=[1,2,1],le='exR=0')
p.plot(iqwR[1:],sy=0,li=[1,2,1])
iqwR=js.dL([transrotsurfModel(w, q=q, Dt=Dtrans, Dr=Drot, exR=1, tau=0.15, rmsd=0.3) for q in ql])
p.plot(iqwR[0],sy=0,li=[1,2,2],le='exR=1')
p.plot(iqwR[1:],sy=0,li=[1,2,2])
iqwR=js.dL([transrotsurfModel(w, q=q, Dt=Dtrans, Dr=Drot, exR=1.4, tau=0.15, rmsd=0.3) for q in ql])
p.plot(iqwR[0],sy=0,li=[3,3,3],le='exR=1.4')
p.plot(iqwR[1:],sy=0,li=[3,3,3])
p.yaxis(min=1e-4,max=10,label=r'I(q,\xw\f{})',scale='l',ticklabel=['power',0,1])
p.xaxis(min=0.1,max=100,label=r'\xw\f{} / ns\S-1',scale='l')
p.legend(x=0.5,y=0.001)
p[0].line(1,5e-2,1,5e-3,2,arrow=1)
p.text('resolution',x=0.9,y=7e-3,rot=90)
p.text('q=0.1 nm\S-1',x=0.2,y=6,rot=0)
p.text('q=20 nm\S-1',x=0.2,y=0.04,rot=0)
p[0].line(0.17,6,0.17,0.04,2,arrow=2)
p.text(r'Variation \nfixed/harmonic protons',x=0.5,y=2e-3,rot=0)
p[0].line(1.4,2.3e-3,3,2.3e-3,arrow=2)

#p.save('Ribonuclease_inelasticNeutronScattering.png',size=(1200,1200),dpi=150)

