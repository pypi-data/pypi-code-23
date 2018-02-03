# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

r"""
Models describing dynamic processes mainly for inealstic neutron scattering.

- Models in the time domain have a parameter t for time. -> intermediate scattering function I(q,t)
- Models in the frequency domain have a parameter w for frequency and _w in the name. -> dynamic structure factor S(q,w)

Models in time domain can be transformed to frequncy domain by :py:func:`~.dynamic.time2frequencyFF`.

In time domain the combination of processes is done by multiplication, including instrument resolution.

:math:`I_x(t,q)=I_1(t,q)I_2(t,q)R(t,q)`.
::

 # multiplying and creating new dataArray
 Ix(q,t) = js.dA( np.c[t, I1(t,q,..).Y*I2(t,q,..).Y*R(t,q,..).Y ].T)

In frequency domain it is a convolution, including the instrument resolution.

:math:`S_x(t,q) = S_1(t,q) \otimes S_2(t,q) \otimes R(w,q)`.
::

 conv=js.formel.convolve
 Sx(q,w)=conv(conv(S1(w,q,..),S2(w,q,..)),res(w,q,..),normB=True)      # normB normalizes resolution

:py:func:`time2frequencyFF` allows mixing between timedomain and frequncy domain models.
This FFT from timedomain needs the resolution included in the timedomain as it acts like a
window function to reduce spectral leakage with vanishing values at :math:`t_{max}`.

The last step is to shift the model spectrum to the symmetry as found in the resolution measurement
and do the binning over frequency channels by :py:func:`~.dynamic.shiftAndBinning`.


Let us describe the diffusion of a particle inside a diffusing invisible sphere by mixing time domain and frequency domain.
::

 start={'s0':5,'m0':0,'a0':1,'bgr':0.00}
 w=np.r_[-100:100:0.5]
 resolution=js.dynamic.resolution_w(w,**start)
 # model
 def diffindiffSphere(w,q,R,Dp,Ds,w0,bgr):
     # time domain with transform to frequency domain
     diff_w=js.dynamic.time2frequencyFF(js.dynamic.simpleDiffusion,resolution,q=q,D=Ds)
     # last convolution in frequency domain, resolution was already included in time domain.
     Sx=js.formel.convolve(js.dynamic.diffusionInSphere_w(w=w,q=q,D=Dp,R=R),diff_w)
     Sxsb=js.dynamic.shiftAndBinning(Sx,w=w,w0=w0)
     Sxsb.Y+=bgr       # add background
     return Sxsb
 #
 Iqw=diffindiffSphere(w=w,q=5.5,R=0.5,Dp=1,Ds=0.035,w0=1,bgr=1e-4)

For more complex systems with different scattering length or changing contributions the fraction of
contributing atoms (with scattering length) has to be included.

Accordingly, if desired, the mixture of coherent and incoherent scattering needs to be accounted for.
This additionally is dependent on the used instrument e.g. for spin echo only 1/3 of the incohernet scattering
contributes to the signal.
An example model for protein dynamics is given in :ref:`Protein incoherent scattering in frequency domain`.

A comparison of different dynamic models in frequency domain is given in examples.
:ref:`A comparison of different dynamic models in frequency domain`.

For conversion to energy use E=js.dynamic.h*w with  h=4135.667662340164 [meV/ns]

Return values are dataArrays were useful.
To get only Y values use .Y

"""

from __future__ import division

import inspect
import numpy as np
import os
import scipy
import scipy.integrate
import scipy.special as special
from scipy.misc import factorial
import scipy.interpolate
import math
import sys


from . import dataArray as dA
from . import dataList as dL
from . import formel
from . import parallel
from .formel import convolve

pi=np.pi
_path_=os.path.realpath(os.path.dirname(__file__))

#: Planck constant in meV/ns
h = scipy.constants.Planck/scipy.constants.e*1E18 # meV*psec
try:
    # change in scipy 18
    spjn=special.spherical_jn
except:
    spjn = lambda n, z: special.jv(n + 1 / 2, z) * np.sqrt(pi / 2) / (np.sqrt(z))

# normalized Gaussian
_gauss=lambda x,mean,sigma:np.exp(-0.5*(x-mean)**2/sigma**2)/np.sqrt(2*pi)/sigma

def simpleDiffusion(q,t,D,amplitude=1):
    """
    Intermediate scattering function for diffusing particles.

    Parameters
    ----------
    q : float, array
        wavevector
    t : float, array
        times
    amplitude : float
        prefactor
    D : float
        diffusion coefficient in units [ [q]**-2/[t] ]

    Returns
    -------
    dataArray

    Notes
    -----
    .. math:: I(q,t)=Ae^{-q^2Dt}

    """
    result=dA(np.c_[t,amplitude*np.exp(-q**2*D*t)].T)
    result.amplitude=amplitude
    result.Diffusioncoefficient=D
    result.wavevector=q
    result.columnname='t;Iqt'
    result.setColumnIndex(iey=None)
    result.modelname=inspect.currentframe().f_code.co_name
    return result

# relaxation with 2 diffusion processes
def doubleDiffusion(q,t,amplitude0,D0,amplitude1=0,D1=0):
    """
    Two exponential decaying functions.

    Parameters
    ----------
    q : float, array
        wavevector
    t : float, array
        timelist
    amplitude0,amplitude1 : float
        prefactor
    D0,D1 : float
        diffusion coefficient in units [ [q]**-2/[t] ]

    Returns
    -------
    dataArray

    """
    result=dA(np.c_[t,amplitude0*np.exp(-q**2*D0*t)+amplitude1*np.exp(-q**2*D1*t)].T)
    result.amplitude0=amplitude0
    result.D0=D0
    result.wavevector=q
    result.amplitude1=amplitude1
    result.D1=D1
    result.modelname=inspect.currentframe().f_code.co_name
    result.columnname = 't;Iqt'
    result.setColumnIndex(iey=None)
    return result

def cumulantDiff(t,q,k0=0,k1=0,k2=0,k3=0,k4=0,k5=0):
    """
    Cumulant of order ki with cumulants as diffusion coefficients.

    means gamma_1 =q^2*D_1 in the linear term
    k0*(exp(-q**2.*(k1*x+1/2*(k2*x)**2+1/6*(k3*x)**3+1/24*(k4*x)**4+1/120*(k5*x)**5)))

    Parameters
    ----------
    t : array
        time
    q : float
        wavevector
    k0 : float
        amplitude
    k1 : float
        diffusion coefficient in units of 1/([q]*[t])
    k2,k3,k4,k5 : float
        higher coefficients in same units as k1

    Returns
    -------
    dataArray :

    """
    t=np.atleast_1d(t)
    res=k0*(
        np.exp(-q**2.*(k1*t+1/2.*abs(k2)*k2*t*t+1./6*k3*k3*k3*t*t*t+1./24*abs(k4)*k4*k4*k4*t*t*t*t+1./120*(k5*t)**5)))
    result=dA(np.c_[t,res].T)
    result.k0tok5=[k0,k1,k2,k3,k4,k5]
    result.wavevector=q
    result.modelname=inspect.currentframe().f_code.co_name
    result.columnname = 't;Iqt'
    result.setColumnIndex(iey=None)
    return result

def cumulant(x,k0=0,k1=0,k2=0,k3=0,k4=0,k5=0):
    """
    Cumulant of order ki
    k0*(exp(-k1*x+1/2*(k2*x)**2-1/6*(k3*x)**3+1/24*(k4*x)**4-1/120*(k5*x)**5))

    Parameters
    ----------
    x : float
        wavevector
    k0,k1, k2,k3,k4,k5 : float
        coefficients all in units 1/x
        k2/k1 = relative standard deviation if a gaussian distribution is assumed
        k3/k1 = relative skewness k3=skewness**3/G**3

    Returns
    -------
    dataArray

    """
    x=np.atleast_1d(x)
    res=k0*np.exp(-k1*x+1/2.*(k2*x)**2-1/6.*(k3*x)**3+1/24*(k4*x)**4-1/120*(k5*x)**5)
    result=dA(np.c_[x,res].T)
    result.k0tok5=[k0,k1,k2,k3,k4,k5]
    result.modelname=inspect.currentframe().f_code.co_name
    result.columnname = 't;Iqt'
    result.setColumnIndex(iey=None)
    return result

def cumulantDLS(t,A,G,sigma,skewness=0,bgr=0.):
    """
    Cumulant analysis for dynamic light scattering

    A*np.exp(-t/G)*(1+(sigma/G*t)**2/2.-(skewness/G*t)**3/6.)+elastic

    Parameters
    ----------
    t : array
        time
    A : float
        Amplitude at t=0; Intercept
    G : float
        Mean relaxation time as 1/decay rate in units of t
    sigma : float
        - relative standard deviation if a gaussian distribution is assumed
        - should be smaller 1 or the Taylor expansion is not valid
        - k2=variance=sigma**2/G**2
    skewness : float,default 0
        relative skewness k3=skewness**3/G**3
    bgr : float; default 0
        a constant background

    Returns
    -------
    dataArray

    References
    ----------
    .. [1] Revisiting the method of cumulants for the analysis of dynamic light-scattering data
          Barbara J. Frisken APPLIED OPTICS  40, 4087 (2001)

    """
    t=np.atleast_1d(t)
    if skewness==0:
        res=A*np.exp(-t/G)*(1+(sigma/G*t)**2/2.)+bgr
    else:
        res=A*np.exp(-t/G)*(1+(sigma/G*t)**2/2.-(skewness/G*t)**3/6.)+bgr
    result=dA(np.c_[t,res].T)
    result.A=A
    result.relaxationtime=G
    result.sigma=sigma
    result.skewness=skewness
    result.elastic=bgr
    result.modelname=inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='t;Iqt'
    return result

def stretchedExp(t,gamma,beta,amp=1):
    """
    Stretched exponential function.

    Parameters
    ----------
    t : array
        times
    gamma : float
        relaxation rate in units 1/[unit t]
    beta : float
        stretched exponent
    amp : float default 1
        amplitude

    Returns
    -------
    dataArray

    """
    t=np.atleast_1d(t)
    res=amp*np.exp(-(t*gamma)**beta)
    result=dA(np.c_[t,res].T)
    result.amp=amp
    result.gamma=gamma
    result.beta=beta
    result.modelname=inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='t;Iqt'
    return result

def jumpDiffusion(t,Q,t0,l0):
    """
    Incoherent intermediate scattering function of translational jump diffusion in the time domain.

    Parameters
    ----------
    t : array
        list of times, units ns
    Q : float
        wavevector, units nm
    t0 : float
        residence time, units ns
    l0 : float
        mean square jump length, units nm

    Returns
    -------
    dataArray

    References
    ----------
    .. [1]  Experimental determination of the nature of diffusive motions of water molecules at low temperatures
            J. Teixeira, M.-C. Bellissent-Funel, S. H. Chen, and A. J. Dianoux
            Phys. Rev. A 31, 1913 – Published 1 March 1985

    """
    t=np.atleast_1d(t)
    D=l0**2/6./t0
    gamma=D*Q*Q/(1+D*Q*Q*t0)

    tdif=np.exp(-gamma*t)
    result=dA(np.c_[t,tdif].T)
    result.residencetime=t0
    result.jumplength=l0
    result.diffusioncoefficient=D
    result.modelname=inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='t;Iqt'
    return result

def methylRotation(t, q,t0=0.001, rhh=0.12, beta=0.8):
    r"""
    Incoherent intermediate scattering function of CH3 methyl rotation in the time domain.

    Parameters
    ----------
    t : array
        List of times, units ns
    q : float
        Wavevector, units nm
    t0 : float, default 0.001
        Residence time, units ns
    rhh : float, default=0.12
        Mean square jump length, units nm
    beta : float, default 0.8
        exponent


    Returns
    -------
    dataArray

    Notes
    -----
    According to [1]_:

    .. math:: I(q,t) = (EISF + (1-EISF) e^{-(\frac{t}{t_0})^{\beta}} )

    .. math:: EISF=\frac{1}{3}+\frac{2}{3}\frac{sin(qr_{HH})}{qr_{HH}}

    with
    :math:`t_0` residence time,
    :math:`r_{HH}` proton jump distance.

    Examples
    --------

     import jscatter as js
     import numpy as np
     # make a plot of the spectrum
     w=np.r_[-100:100]
     ql=np.r_[1:15:1]
     iqwCH3=js.dL([js.dynamic.time2frequencyFF(js.dynamic.methylRotation,'elastic',w=np.r_[-100:100:0.1],dw=0,q=q ) for q in ql])
     p=js.grace()
     p.plot(iqwCH3,le='CH3')
     p.yaxis(min=1e-5,max=10,scale='l')

    References
    ----------
    .. [1] M. Bée, Quasielastic Neutron Scattering (Adam Hilger, 1988).

    """
    t=np.atleast_1d(t)
    EISF=(1+2*np.sinc(q*rhh))/3.
    Iqt=(1-fraction)+fraction*(EISF+(1-EISF)*np.exp(-(t/t0)**beta))

    result=dA(np.c_[t,Iqt].T)
    result.wavevector=q
    result.residencetime=t0
    result.rhh=rhh
    result.beta=beta
    result.EISF=EISF
    result.methylfraction=fraction
    result.modelname=inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='t;Iqt'
    return result

def diffusionHarmonicPotential(t,q,rmsd,tau,ndim=3):
    """
    ISF corresponding to the standard OU process for diffusion in harmonic potential for dimension 1,2,3.

    The intermediate scattering function corresponding to the standard OU process
    for diffusion in an harmonic potenital [1]_. It is used for localized translational motion in
    incoherent neutron scattering [2]_ as improvement for the diffusion in a sphere model.
    Atomic motion may be resticted to ndim=1,2,3 dimensions and are isotropical averaged.
    The correlation is assumed to be exponential decaying.

    Parameters
    ----------
    t : array
        timevalues in units ns
    q : float
        wavevector in unit 1/nm
    rmsd : float
        Root mean square displacement <u**2>**0.5 in potetial in units nm.
        <u**2>**0.5 is the width of the potential
        According to [2]_  5*u**2=R**2 compared to the diffusion in a sphere.
    tau : float
        Correlation time in units ns.
        Diffusion constant in sphere Ds=u**2/tau
    ndim : 1,2,3, default=3
        Dimensionality of the diffusion potential.

    Returns
    -------
        dataArray

    Examples
    --------
    ::

     import numpy as np
     import jscatter as js
     t=np.r_[0.1:6:0.1]
     p=js.grace()
     p.plot(js.dynamic.diffusionHarmonicPotential(t,1,2,1,1),le='1D ')
     p.plot(js.dynamic.diffusionHarmonicPotential(t,1,2,1,2),le='2D ')
     p.plot(js.dynamic.diffusionHarmonicPotential(t,1,2,1,3),le='3D ')
     p.legend()
     p.yaxis(label='I(Q,t)')
     p.xaxis(label='Q / ns')
     p.subtitle('Figure 2 of ref Volino J. Phys. Chem. B 110, 11217')

    References
    ----------
    .. [1] Quasielastic neutron scattering and relaxation processes in proteins: analytical and simulation-based models
           G. R. Kneller Phys. ChemChemPhys. ,2005, 7,2641–2655
    .. [2] Gaussian model for localized translational motion: Application to incoherent neutron scattering
           F. Volino, J.-C. Perrin and S. Lyonnard, J. Phys. Chem. B 110, 11217–11223 (2006)

    """
    erf = special.erf
    erfi=special.erfi
    q2u2=q**2*rmsd**2
    ft=(1 - np.exp(-t / tau))
    ft[t==0]=1e-8 # avoid zero to prevent zero divison and overwrite later with EISF
    if ndim==3:
        Iqt=np.exp(-q2u2*ft)
        EISF=np.exp(-q2u2)
        Iqt[t==0]=EISF
    elif ndim==2:
        q2u2exp = q2u2 * ft
        Iqt=0.5*pi**0.5 * np.exp(-q2u2exp) * erfi(q2u2exp**0.5) / q2u2exp**0.5
        EISF=0.5*pi**0.5 * np.exp(-q2u2) * erfi(q2u2**0.5) / q2u2**0.5
        Iqt[t==0]=EISF
    elif ndim==1:
        q2u2exp = q2u2 * ft
        Iqt=0.5*pi**0.5 *  erf(q2u2exp**0.5) / q2u2exp**0.5
        EISF = 0.5 * pi ** 0.5 * erf(q2u2 ** 0.5) / q2u2 ** 0.5
        Iqt[t==0]=EISF
    else:
        raise Exception('ndim should be one of 1,2,3 ')

    result=dA(np.c_[t,Iqt].T)
    result.tau=tau
    result.Ds=rmsd**2/tau
    result.rmsd=rmsd
    result.EISF=EISF
    result.wavevector=q
    result.dimension=ndim
    result.modelname=inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='t;Iqt'
    return result

def finiteZimm(t,q,NN=None,pmax=None,ll=None,Dcm=None,Dcmfkt=lambda q:1.,tintern=0.,mu=0.5,viscosity=1.,Temp=293):
    """
    Zimm dynamics with internal friction of a finite chain with N beads of bonds length l. Coherent scattering.

    The Zimm model describes the conformational dynamics of an ideal chain with hydrodynamic interaction between beads.
    The single chain diffusion is represented by Brownian motion of beads connected by harmonic springs.
    no excluded volume, random thermal force, drag force with solvent, hydrodynamics between beads
    and optional internal friction.

    Parameters
    ----------
    t : array
        Time in nanoseconds
    q: float, array
        Scattering vector  in nm^-1
        If q is list a dataList is returned  otherwise a dataArray is returned
    NN : integer
        Number of chain beads
    ll : float, default 1
        Bond length between beads; units nm
    pmax : integer, default is NN
        - integer => maximum mode number
        - list    => list of amplitudes>0 for individual modes
          to allow weighing; not given modes have weigth zero
    Dcm : float
        Center of mass diffusion in nm^2/ns
         - 0.196 kb T/(Re*viscosity)  theta solvent with mu=0.6
         - 0.203 kb T/(Re*viscosity)  good solvent  with mu=0.5
    Dcmfkt : function returning array
        Function to modify Dcm as Dcm(q)=Dcm*Dcmfkt(q) e.g. for inclusion of structure factor Dcmfkt=lambda q:1/S(q)
    tintern : float>0
        Additional relaxation time due to internal friction
        (if a tuple as (0,1,1,1,) the mode p will get tintern[p])
        Automatically extended to length pmax
    mu : float in range [0.5,0.6]
        varies between good solvent 0.6 and theta solvent 0.5 (gaussian chain)
    viscosity : float
        cPoise=mPa*s  as water 20+273.15 K =1 mPa*s
    Temp : float
        temperatur  Kelvin = 273+20

    Returns
    -------
     dataArray : for single q
      - [wavevector q , Iqt_diff+modes, Iqt_diffusion]
      - dataArray.modecontribution of modes i in sequence
     dataList : multiple q
      -   datalist with dataArrays as for single q as above

    Notes
    -----
    Additional attributes defined:
     - Re   end to end distance  Re^2=l^2*N^2mu
     - tz1  rotational corrleation time tz1 = visc*Re^3/(sqrt(3 pi)kb*T)
     - t_p  characteristic times t_p=tz1*p^-3mu+tintern
     - modecontribution is modecontribution as in PRL 71, 4158 equ (3)

    From above the triple Dcm,ll,NN are fixed.
     - If 2 are given 3rd is calculated
     - If all 3 are given the given values are used


    References
    ----------
    .. [1]  Doi Edwards Theory of Polymer dynamics
            in appendix the equation is found
    .. [2]  Nonflexible Coils in Solution: A Neutron Spin-Echo Investigation of
            Alkyl-Substituted Polynorbonenes in Tetrahydrofuran
            Michael Monkenbusch et al Macromolecules 2006, 39, 9473-9479
            The exponential is missing a "t"
            http://dx.doi.org/10.1021/ma0618979

    about internal friction

    .. [3]  Exploring the role of internal friction in the dynamics of unfolded proteins using simple polymer models
            Cheng et al JOURNAL OF CHEMICAL PHYSICS 138, 074112 (2013)  http://dx.doi.org/10.1063/1.4792206
    .. [4]  Rouse Model with Internal Friction: A Coarse Grained Framework for Single Biopolymer Dynamics
            Khatri, McLeish|  Macromolecules 2007, 40, 6770-6777  http://dx.doi.org/10.1021/ma071175x

    mode contribution factors from

    .. [5]  Onset of Topological Constraints in Polymer Melts: A Mode Analysis by Neutron Spin Echo Spectroscopy
            D. Richter et al PRL 71,4158-4161 (1993)

    """
    kb=1.3806505e-23   # in SI units
    # convert to Pa*s
    viscosity*=1e-3
    # assure flatt arrays
    t=np.atleast_1d(t)
    q=np.atleast_1d(q)
    # check mu between 0.5 and 0.6
    mu=max(mu,0.5)
    mu=min(mu,0.6)
    # avoid ll=0 from stupid users
    if ll==0: ll=None
    # and linear interpolate prefactor
    fact=0.196+(mu-0.5)/(0.6-0.5)*(0.203-0.196)
    NN=int(NN)
    if pmax==None: pmax=NN
    # if a list pmax of modes is given these are amplitudes for the modes
    # pmax is length of list
    if isinstance(pmax,(int,float)):
        pmax=min(int(pmax),NN)
        ps=range(1,pmax+1)
        modeamplist=np.ones_like(ps)
    elif isinstance(pmax,list):
        ps=range(1,len(pmax)+1)
        modeamplist=np.abs(pmax)
    else:
        raise TypeError('pmax should be integer or list of amplitudes')

    # calc the cases of not given parameters for Dcm,NN,ll
    if Dcm is None and ll is not None and NN is not None:
        Re=np.sqrt(ll**2*NN**(2*mu))                  # end to end distance
        Dcm=fact*kb*Temp/(Re*1e-9*viscosity)*1e9     # diffusion constant  in nm^2/ns
    elif Dcm is not None and ll is None and NN is not None:
        Re=fact*kb*Temp/(Dcm*1e-9*viscosity)*1e9     # end to end distance
        ll=Re/NN**mu                                 # bond length
    elif Dcm is not None and ll is not None and NN is None:
        Re=fact*kb*Temp/(Dcm*1e-9*viscosity)*1e9     # end to end distance
        NN=int((Re/ll)**(1./mu))
    elif Dcm is not None and ll is not None and NN is not None:
        Re=np.sqrt(ll**2*NN**(2*mu))
    else:
        raise TypeError('fqtfiniteZimm takes at least 2 arguments from Dcm,NN,ll')
    # slowest zimm time
    tz1=viscosity*(Re*1e-9)**3/(np.sqrt(3*pi)*kb*Temp)*1e9
    # characteristic Zimm time of mode p with internal friction ti
    if isinstance(tintern,tuple): # allow different tintern
        tintern=(tintern+(tintern[-1],)*len(modeamplist))[:len(modeamplist)]
        # remember p starts at 1
        tzp=lambda p,ti=1:tz1*p**(-3*mu)+abs(tintern[p-1])*ti
    elif isinstance(tintern,(float,int)): # for a common tintern
        tzp=lambda p,ti=1:tz1*p**(-3*mu)+abs(tintern)*ti
    else:
        raise TypeError('tintern should be float or tuple as (1,2,3) of float')
    # define functions
    spmax=lambda t,NN,n,m,mu,moAmplist,ps:[
        4*Re**2/pi**2*pamplitude*(1./(ip**(2*mu+1))*
                                     np.cos(pi*ip*n/NN)*np.cos(pi*ip*m/NN)*
                                     (1-np.exp(-t/(tzp(ip)))))
        for ip,pamplitude in zip(ps,moAmplist)]
    # calc array of mode contributions including first constant element as list
    Bmn=lambda t,NN,l,mu:np.array([[np.array([abs(n-m)**(2*mu)*l**2]*len(t))]+spmax(t,NN,n,m,mu,modeamplist,ps)
                                   for n in range(1,NN+1) for m in range(1,NN+1)])
    # do the calculation as an array of bnm=[n*m ,pmax, len(t)] elements
    bnm=Bmn(t,NN,ll,mu)
    # sum up contributions for modes: all, diff+ mode1, only diffusion, t=0 amplitude for normalisation
    BNM=np.sum(bnm[:,:,:],axis=1)            # summation over pmax axis
    BNM0=bnm[:,:1,0]                        # only 0. element for t=0
    bmninf=Bmn(np.r_[tzp(1,0)*1e6],NN,ll,mu) # relaxed after long time for t=inf
    BNMinf=np.sum(bmninf[:,:],axis=1)        # summation over pmax axis again
    BNMmcontrib=bmninf[:,1:]+bmninf[:,0:1,:]    # t=0 contrib + single modes contrib
    result=dL()
    for qq in q:
        # diffusion for all t
        Sqt=np.exp(-qq**2*Dcm*Dcmfkt(qq)*t)                 # only diffusion contribution
        # amplitude at t=0
        expB0=np.sum(np.exp(-qq**2/6.*BNM0))                # is S(qq,t=0)/Sqt
        # diffusion for infinite times in modes
        expBinf=np.sum(np.exp(-qq**2/6.*BNMinf))            # is S(qq,t=inf)/Sqt
        # contribution all modes
        expB=np.sum(np.exp(-qq**2/6.*BNM),axis=0)
        # contribution only first modes
        result.append(dA(np.r_[[t,Sqt*expB/expB0,
                                Sqt*expBinf/expB0,
                                ]]))
        result[-1].modecontribution=(np.sum(np.exp(-qq**2/6.*BNMmcontrib),axis=0)/expB0).flatten()
        result[-1].q=qq
        result[-1].Re=Re
        result[-1].ll=ll
        result[-1].pmax=pmax
        result[-1].Dcm=Dcm
        result[-1].effectiveDCM=Dcm*Dcmfkt(qq)
        DZimm=fact*kb*Temp/(Re*1e-9*viscosity)*1e9
        result[-1].DZimm=DZimm
        result[-1].mu=mu
        result[-1].viscosity=viscosity
        result[-1].Temperature=Temp
        result[-1].tzimm=tz1
        result[-1].tintern=tintern
        result[-1].modeAmplist=modeamplist
        result[-1].Drot=1./6./tz1
        result[-1].N=NN
        result[-1].columnname=' time; Sqt; Sqt_inf'
    if len(result)==1:
        return result[0]
    result.setColumnIndex(iey=None)
    result.modelname=sys._getframe().f_code.co_name
    # update parameter
    return result

def finiteRouse(t,q,NN=None,pmax=None,ll=None,frict=None,Dcm=None,Wl4=None,Dcmfkt=lambda q:1.,tintern=0.,Temp=293):
    """
    Rouse dynamics of a finite chain with N beads of bonds length l and internal friction. Coherent scattering.

    The Rouse model describes the conformational dynamics of an ideal chain.
    The single chain diffusion is represented by Brownian motion of beads connected by harmonic springs.
    no excluded volume, random thermal force, drag force with solvent and optional internal friction.


    Parameters
    ----------
    t : array
        time in nanoseconds
    q : array
        scattering vector          nm^-1
        if q is list a dataList is returned
        otherwise a dataArray is returned
    NN : integer
        number of chain beads
    ll : float, default 1
        bond length between beads; unit nm
    pmax : integer
        as integer => maximum mode number default  is NN
        as list =>list of amplitudes>0 for individual modes
        to allow weighting; not given modes have weigth zero
    frict : float
        friction of a bead
    Wl4 : float
        needed to calc friction and Dcm
    Dcm : float
        Center of mass diffusion in nm^2/ns
         - =kT/NN/f     with f =solvent friction
         - =Wl^4/(3*N*l^2)=Wl^4/(3* Re^2)
    Dcmfkt : function returning array
        function to modify Dcm as Dcm(q)=Dcm*Dcmfkt(q)
        eg for inclusion of structure factor Dcmfkt=lambda q:1/S(q)
    tintern : float>0
        relaxation time due to internal friction  in ns
    Temp : float
        temperature  Kelvin = 273+T[°C]

    Returns
    -------
    dataArray

    Notes
    -----
    Additional Attributes
     - Wl4
     - Re  end to end distance Re^2=l^2*N
     - tr1 is rotational corrleation time or rouse time tr1 = f*NN^2*ll^2/(3 pi^2*kb*T)= <Re^2>/(3*pi*Dcm)
     - tintern relaxation time due to internal friction
     - t_p characteristic times   t_p=tr1*p^2+tintern

    From above the triple Dcm,ll,NN are fixed.
     - If 2 are given 3rd is calculated
     - If all 3 are given the given values are used

    References
    ----------
    .. [1]  Doi Edwards Theory of Polymer dynamics
            in the appendix the equation is found
    .. [2]  Nonflexible Coils in Solution: A Neutron Spin-Echo Investigation of
            Alkyl-Substituted Polynorbonenes in Tetrahydrofuran
            Michael Monkenbusch et al Macromolecules 2006, 39, 9473-9479
            The exponential is missing a "t"
            http://dx.doi.org/10.1021/ma0618979

    about internal friction

    .. [3]  Exploring the role of internal friction in the dynamics of unfolded proteins using simple polymer models
            Cheng et al JOURNAL OF CHEMICAL PHYSICS 138, 074112 (2013)  http://dx.doi.org/10.1063/1.4792206
    .. [4]  Rouse Model with Internal Friction: A Coarse Grained Framework for Single Biopolymer Dynamics
            Khatri, McLeish|  Macromolecules 2007, 40, 6770-6777  http://dx.doi.org/10.1021/ma071175x

    """
    kb=1.3806505e-23   # in SI units
    # assure flatt arrays
    t=np.atleast_1d(t)
    q=np.atleast_1d(q)
    # avoid ll=0
    if ll==0: ll=None
    NN=int(NN)
    if pmax is None: pmax=NN
    # if a list pmax of modes is given these are amplitudes for the modes
    # pmax is length of list
    if isinstance(pmax,(int,float)):
        pmax=min(int(pmax),NN)
        ps=range(1,pmax+1)
        modeamplist=np.ones_like(ps)
    elif isinstance(pmax,list):
        ps=range(1,len(pmax)+1)
        modeamplist=pmax
    else:
        raise TypeError('pmax should be integer or list of amplitudes')
    # calc the cases of not given parameters for Dcm,NN,ll
    Re=ll*np.sqrt(NN)                  # end to end distance
    if Dcm is not None and frict is None:
        frict=kb*Temp/NN/(Dcm*1e9)     # diffusion constant  in nm^2/ns
    elif Dcm is None and frict is not None:
        Dcm=kb*Temp/NN/frict/1e9     # diffusion constant  in nm^2/ns
    elif Dcm is None and frict is None and Wl4 is not None:
        Dcm=Wl4/(3*Re**2)
        frict=kb*Temp/NN/(Dcm*1e9)
    else:
        raise TypeError('fqtfiniteRouse takes at least 1 arguments from Dcm,frict')
    # slowest rouse time
    tr1=Re**2/(3*pi**2*Dcm)
    # characteristic rouse time of mode p with internal friction ti
    trp=lambda p,ti=tintern:tr1/p**(-2)+abs(ti)
    # define functions
    spmax=lambda t,NN,n,m,moAmplist,ps:[
        4*Re**2/pi**2*pamplitude*(1./(ip**2)*
                                     np.cos(pi*ip*n/NN)*np.cos(pi*ip*m/NN)*
                                     (1-np.exp(-t/(trp(ip)))))
        for ip,pamplitude in zip(ps,modeamplist)]
    # B=lambda t,NN,l,n,m:abs(n-m)*l**2+sumpmax(t,NN,n,m)
    # Bmn=lambda t,NN,l:np.array([B(t,NN,l,n,m) for n in range(1,NN+1) for m in range(1,NN+1)])
    Bmn=lambda t,NN,l:np.array([[np.array([abs(n-m)*l**2]*len(t))]+spmax(t,NN,n,m,modeamplist,ps)
                                for n in range(1,NN+1) for m in range(1,NN+1)])
    # do the calculation as an array of bnm=[n*m ,pmax, len(t)] elements
    bnm=Bmn(t,NN,ll)

    BNM=np.sum(bnm[:,:,:],axis=1)            # summation over pmax axis
    BNM0=bnm[:,:1,0]                        # only 0. element for t=0
    bmninf=Bmn(np.r_[trp(1,0)*1e6],NN,ll) # relaxed after long time for t=inf
    BNMinf=np.sum(bmninf[:,:],axis=1)        # summation over pmax axis again
    BNMmcontrib=bmninf[:,1:]+bmninf[:,0:1,:]    # t=0 contrib + single modes contrib
    result=dL()
    for qq in q:
        # diffusion for all t
        Sqt=np.exp(-qq**2*Dcm*Dcmfkt(qq)*t)                       # only diffusion contribution
        # amplitude at t=0
        expB0=np.sum(np.exp(-qq**2/6.*BNM0))# /float(NN)            # is S(qq,t=0)/Sqt
        # diffusion for infinite times in modes
        expBinf=np.sum(np.exp(-qq**2/6.*BNMinf))# /float(NN)        # is S(qq,t=inf)/Sqt
        # contribution all modes
        expB=np.sum(np.exp(-qq**2/6.*BNM),axis=0)# /float(NN)
        # contribution only first modes
        result.append(dA(np.r_[[t,Sqt*expB/expB0,
                                Sqt*expBinf/expB0,
                                ]]))
        result[-1].setColumnIndex(iey=None)
        result[-1].modecontribution=(np.sum(np.exp(-qq**2/6.*BNMmcontrib),axis=0)/expB0).flatten()
        result[-1].q=qq
        result[-1].Re=Re
        result[-1].ll=ll
        result[-1].pmax=pmax
        result[-1].Dcm=Dcm
        result[-1].Dcmrouse=kb*Temp/NN/frict/1e9
        result[-1].Temperature=Temp
        result[-1].trouse=tr1
        result[-1].tintern=tintern
        result[-1].friction=frict
        result[-1].Drot=1./6./tr1
        result[-1].N=NN
        result[-1].columnname='time[ns]; Sqt; Sqt_inf'
    if len(result)==1:
        return result[0]
    result.setColumnIndex(iey=None)
    result.modelname=inspect.currentframe().f_code.co_name
    # update parameter
    return result

def diffusionPeriodicPotential(t,q,u,rt,Dg,gamma=1,NN=100):
    """
    Fractional diffusion of a particle in a periodic potential.

    The diffusion describes a fast dynamics inside of the potential trap with a mean square displacement
    before a jump and a fractional long time diffusion. For fractional coefficient gamma=1 normal diffusion
    is recovered.

    Parameters
    ----------
    t : array
        Time points
    q : float
        Wavevector
    u : float
        Mean displacement in the trap
    rt : float
        Relaxation time of fast dynamics in the trap (1/lambda in [1]_ )
    gamma : float
        Fractional exponent gamma=1 is normal diffusion
    Dg : float
        Long time fractional diffusion coefficient
    NN : int, default 100
        Order for approximating Mittag Leffler function
        sum([x**k/scipy.special.gamma(a*k+1) for k in range(NN)])
        Test this for your needed time range. See Examples

    Returns
    -------
    dataArray : .
        [times, intermediate scattering function , intermediate scattering function only diffusional part]

    References
    ----------
    .. [1] Gupta, S.; Biehl, R.; Sill, C.; Allgaier, J.; Sharp, M.; Ohl, M.; Richter, D.
           Macromolecules 2016, 49 (5), 1941.


    Examples
    --------
    ::

     t=js.loglist(1,10000,1000)
     q=0.5
     p=js.grace()
     f100=js.dynamic.diffusionPeriodicPotential(t,q,0.5,15,0.036,NN=100)
     f30=  js.dynamic.diffusionPeriodicPotential(t,q,0.5,15,0.036,NN=30)
     p.plot(f100,legend='NN=100')
     p.plot(f100,legend='NN=30')

    """
    Ea=formel.Ea
    # q=np.atleast_1d(q)
    # mean square displacement for diffusion in periodic potential
    msd6=lambda t,Dg,u,rt,gamma=1:Dg*t**gamma/scipy.special.gamma(gamma+1)
    def msd6trap(t,Dg,u,rt,gamma=1):
        res=t*0+u**2
        res[t<rt*30]= u**2*(1-Ea(-(t[t<rt*30]/rt)**gamma, gamma))
        return res

    msd6_0=lambda t,Dg,u,rt,gamma=1:Dg*t**gamma/scipy.special.gamma(gamma+1)+u**2
    # intermediate scattering function of diffusion in periodic...
    sqt=lambda q,t,Dg,u,rt,gamma=1:np.exp(-q**2*(msd6(t,Dg,u,rt,gamma)))
    sqttrap=lambda q,t,Dg,u,rt,gamma=1:np.exp(-q**2*(msd6trap(t,Dg,u,rt,gamma)))
    sqt_0=lambda q,t,Dg,u,rt,gamma=1:np.exp(-q**2*msd6_0(t,Dg,u,rt,gamma))

    result=dA(np.c_[t,sqt(q,t,Dg,u,rt,gamma)*sqttrap(q,t,Dg,u,rt,gamma),sqt_0(q,t,Dg,u,rt,gamma),sqttrap(q,t,Dg,u,rt,gamma)].T)
    result.wavevector=q
    result.fractionalDiffusionCoefficient=Dg
    result.displacement_u=u
    result.relaxationtime=rt
    result.fractionalCoefficient_gamma=gamma
    result.modelname=inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='t;Iqt;Sqt_inf'
    return result

def zilmanGranekBicontinious(t, q, xi, kappa, eta, mt=1, amp=1, eps=1 ,nGauss=60):
    """
    Dynamics of bicontinuous microemulsion phases. Zilman-Granek model as Equ B10 in [1]_. Coherent scattering.

    On very local scales (however larger than the molecular size) Zilman and Granek represent the amphiphile layer
    in the bicontinuous network as consisting of an ensemble of independent patches at random orientation of size
    equal to the correlation length xi.
    Uses Gauss integration and multiprocessing.

    Parameters
    ----------
    t : array
        Time values in ns
    q : float
        Scattering vector in 1/A
    xi : float
        Correlation length related to the size of patches which are locally planar
        and determine the width of the peak in static data. unit A
        A result of the teubnerStrey model to e.g. SANS data. Determines kmin=eps*pi/xi .
    kappa : float
        Apparent single membrane bending modulus, unit kT
    eta : float
        Solvent viscosity, unit kT*A^3/ns=100/(1.38065*T)*eta[unit Pa*s]
        Water about 0.001 Pa*s = 0.000243 kT*A^3/ns
    amp : float, default = 1
        Amplitude scaling factor
    eps : float, default=1
        Scaling factor in range [1..1.3] for kmin=eps*pi/xi and rmax=xi/eps. See [1]_.
    mt : float, default 0.1
        Membrane thickness in unit A as approximated from molecular size of material. Determines kmax=pi/mt.
        About 12 Angstroem for tenside C10E4.
    nGauss : int, default 60
        Number of points in Gauss integration

    Returns
    -------
        dataList

    Notes
    -----
    - For technical reasons, in order to avoid numerical difficulties, the real space upper (rmax integration) cutoff
      was realized by multiplying the integrand with a Gaussian having a width of eps*xi and integrating over [0,3*eps*xi].

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     t=js.loglist(0.1,30,20)
     p=js.grace()
     iqt=js.dynamic.zilmanGranekBicontinious(t=t,q=np.r_[0.03:0.2:0.04],xi=110,kappa=1.,eta=0.24e-3,nGauss=60)
     p.plot(iqt)
     # to use the multiprocessing in a fit of data use memoize
     data=iqt                          # this represent your measured data
     tt=list(set(data.X.flatten))      # a list of all time values
     tt.sort()
     # use correct values from data for q     -> interpolation is exact for q and tt
     zGBmem=js.formel.memoize(q=data.q,t=tt)(js.dynamic.zilmanGranekBicontinious)
     def mfitfunc(t, q, xi, kappa, eta, amp):
        # this will calculate in each fit step for forst Q (but calc all) and then take from memoized values
        res= zGBmem(t=t, q=q, xi=xi, kappa=kappa, eta=eta, amp=amp)
        return res.interpolate(q=q,X=t)[0]
     # use mfitfunc for fitting with multiprocessing


    References
    ----------
    .. [1] Dynamics of bicontinuous microemulsion phases with and without amphiphilic block-copolymers
           M. Mihailescu1, M. Monkenbusch et al
           J. Chem. Phys. 115, 9563 (2001); http://dx.doi.org/10.1063/1.1413509

    """

    tt=np.r_[0.,t]
    qq=np.r_[q]
    result=dL()
    nres=parallel.doForList(_zgbicintegral, looplist=qq,loopover='q', t=tt, xi=xi, kappa=kappa, eta=eta, mt=mt, eps=eps, nGauss=nGauss )
    for qi,res in zip(qq,nres):
        S0=res[0]
        result.append(dA(np.c_[t,res[1:]].T))
        result[-1].setColumnIndex(iey=None)
        result[-1].Y*=amp/S0
        result[-1].q=qi
        result[-1].xi=xi
        result[-1].kappa=kappa
        result[-1].eta=eta
        result[-1].eps=eps
        result[-1].mt=mt
        result[-1].amp=amp
        result[-1].setColumnIndex(iey=None)
        result[-1].columnname = 't;Iqt'

    return result

def _zgbicintegral(t, q, xi, kappa, eta,eps,mt, nGauss):
    """integration of gl. B10 in Mihailescu, JCP 2001"""
    quad=formel.parQuadratureFixedGauss
    aquad = formel.parQuadratureAdaptiveGauss
    def _zgintegrand_k(k,r,t,kappa,eta):
        """kmin-kmax integrand of gl. B10 in Mihailescu, JCP 2001"""
        tmp=-kappa/4./eta*k**3*t
        res= (1.-special.j0(k*r)*np.exp(tmp))/k**3
        return res

    def _zgintegral_k(r,t,xi,kappa,eta):
        """kmin-kmax integration of gl. B10 in Mihailescu, JCP 2001
        integration is doen in 2 intervalls to weigth the lower stronger.
        """
        kmax=pi/mt
        # use higher accuracy at lower k
        res0=aquad(_zgintegrand_k,eps*pi/xi,kmax/8.,'k',r=r,t=t[:,None],kappa=kappa,eta=eta ,rtol=0.1/nGauss,maxiter=250)
        res1=aquad(_zgintegrand_k, kmax/8. ,kmax   ,'k',r=r,t=t[:,None],kappa=kappa,eta=eta ,rtol=1./nGauss,maxiter=250)
        return res0+res1

    def _zgintegrand_mu_r(r,mu,q,t,xi,kappa,eta):
        """Mu-r integration of gl. B10 in Mihailescu, JCP 2001
        aus numerischen Grnden Multiplikation mit Gaussfunktion mit Breite xi"""
        tmp=(-1/(2*pi*kappa)*q*q*mu*mu*_zgintegral_k(r,t,xi,kappa,eta)[0]-r*r/(2*(eps*xi)**2))
        tmp[tmp<-500]=-500  # otherwise owerflow error in np.exp
        y=r*special.j0(q*r*np.sqrt(1-mu**2))*np.exp(tmp-r**2/(2*(eps*xi)**2))
        return y

    def _gaussBorder(mu,q,t,xi,kappa,eta):
        # For technical reasons, in order to avoid numerical difficulties, the real
        # space upper cutoff was realized by multiplying the integrand with a
        # Gaussian having a width of eps*xi.
        y=quad(_zgintegrand_mu_r,0,eps*3*xi,'r',mu=mu,q=q,t=t,xi=xi,kappa=kappa,eta=eta,n=nGauss)
        return y

    y=quad(_gaussBorder, 0., 1.,'mu', q=q, t=t, xi=xi, kappa=kappa, eta=eta, n=nGauss)
    return y

def zilmanGranekLamellar(t,q,df,kappa,eta,mu=0.001,eps=1,amp=1,mt=0.1,nGauss=40):
    """
    Dynamics of lamellar microemulsion phases.  Zilman-Granek model as Equ B10 in [1]_. Coherent scattering.

    Oriented lamellar phases at the length scale of the inter membrane distance and beyond are performed
    using small-angle neutrons scattering and neutron spin-echo spectroscopy.

    Parameters
    ----------
    t : array
        Time in ns
    q : float
        Scattering vector
    df : float
        - film-film distance. unit A
        - This represents half the periodicity of the structure, generally denoted by d=0.5df which determines the peak position.
          and determines kmin=eps*pi/df
    kappa : float
        Apparent single membrane bending modulus, unit kT
    mu : float, default 0.001
        Angle between q and surface normal in unit rad.
        For lamelar oriented system this is close to zero in NSE.
    eta : float
        Solvent viscosity, unit kT*A^3/ns = 100/(1.38065*T)*eta[unit Pa*s]
        Water about 0.001 Pa*s = 0.000243 kT*A^3/ns
    eps : float, default=1
        Scaling factor in range [1..1.3] for kmin=eps*pi/xi and rmax=xi/eps
    amp : float, default 1
        Amplitude scaling factor
    mt : float, default 0.1
        Membrane thickness in unit A as approximated from molecular size of material. Determines kmax=pi/mt
        About 12 Angstroem for  tenside C10E4.
    nGauss : int, default 40
        Number of points in Gauss integration

    Returns
    -------
        dataList

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     t=js.loglist(0.1,30,20)
     ql=np.r_[0.08:0.261:0.03]
     p=js.grace()
     iqt=js.dynamic.zilmanGranekLamellar(t=t,q=ql,df=100,kappa=1,eta=2*0.24e-3)
     p.plot(iqt)

    Notes
    -----
    The integrations are done by nGauss point Gauss quadrature, except for the kmax-kmin integration which is done by
    adaptive Gauss integration with rtol=0.1/nGauss k< kmax/8 and rtol=1./nGauss k> kmax/8.

    References
    ----------
    .. [1] Neutron scattering study on the structure and dynamics of oriented lamellar phase microemulsions
           M. Mihailescu, M. Monkenbusch, J. Allgaier, H. Frielinghaus, D. Richter, B. Jakobs, and T. Sottmann
           Phys. Rev. E 66, 041504 (2002)

    """

    tt=np.r_[0.,t]
    qq=np.atleast_1d(q)
    result=dL()
    nres=parallel.doForList(_zglamintegral, looplist=qq,loopover='q', t=tt,  kappa=kappa, eta=eta, df=df,mu=mu,mt=mt, eps=eps, nGauss=nGauss )
    for qi,res in zip(qq,nres):
        S0=res[0]
        result.append(dA(np.c_[t,res[1:]].T))
        result[-1].setColumnIndex(iey=None)
        result[-1].Y*=amp/S0
        result[-1].q=qi
        result[-1].df=df
        result[-1].kappa=kappa
        result[-1].eta=eta
        result[-1].eps=eps
        result[-1].mt=mt
        result[-1].amp=amp
        result[-1].setColumnIndex(iey=None)
        result[-1].columnname='t;Iqt'

    return result

def _zglamintegral(t, q, df,kappa, eta,eps,mu,mt, nGauss):
    """integration of gl. 16"""
    #quad=scipy.integrate.quad
    quad=formel.parQuadratureFixedGauss
    aquad=formel.parQuadratureAdaptiveGauss
    def _zgintegrand_k(k,r,t,kappa,eta):
        """kmin-kmax integrand o"""
        tmp=-kappa/4./eta*k**3*t
        res= (1.-special.j0(k*r)*np.exp(tmp))/k**3
        return res

    def _zgintegral_k(r,t,df,kappa,eta):
        """
        kmin-kmax integration of gl. B10 in Mihailescu, JCP 2001
        """
        kmax=pi/mt
        # use higher accuracy at lower k
        res0=aquad(_zgintegrand_k,eps*pi/df,kmax/8.,'k',r=r,t=t[:,None],kappa=kappa,eta=eta ,rtol=0.1/nGauss,maxiter=250)
        res1=aquad(_zgintegrand_k, kmax/8. ,kmax   ,'k',r=r,t=t[:,None],kappa=kappa,eta=eta ,rtol= 1./nGauss,maxiter=250)
        return res0+res1

    def _zgintegrand_r(r,mu,q,t,df,kappa,eta):
        """Mu-r integration """
        smu=np.sin(mu)
        tmp=(-1/(2*pi*kappa)*q*q*(1-smu**2)*_zgintegral_k(r,t,df,kappa,eta)[0])
        tmp[tmp<-500]=-500  # otherwise owerflow error in np.exp
        y=r*special.j0(q*r*smu)*np.exp(tmp)
        return y

    y=quad(_zgintegrand_r,0,df/eps,'r',mu=mu,q=q,t=t,df=df,kappa=kappa,eta=eta,n=nGauss)
    return y

def integralZimm(t,q,Temp=293,viscosity=1.0e-3,amp=1,rtol=0.02,tol=0.02,limit=50):
    """
    Conformational dynamics of an ideal chain with hydrodynamic interaction Integral version Zimm dynamics. Coherent scattering.

    The Zimm model describes the conformational dynamics of an ideal chain with hydrodynamic
    interaction between beads. See [1]_.

    Parameters
    ----------
    t : array
        Time points in ns
    q : float
        Wavevector in 1/nm
    Temp : float
        Temperature in K
    viscosity : float
        Viscosity in cP=mPa*s
    amp : float
        Amplitude

    Returns
    -------
        dataArray

    Examples
    --------
    ::

     t=np.r_[0:10:0.2]
     p=js.grace()
     for q in np.r_[0.26,0.40,0.53,0.79,1.06]:
        iqt=js.dynamic.integralZimm(t=t,q=q,viscosity=0.2e-3)
        p.plot(iqt)
        #p.plot((iqt.X*iqt.q**3)**(2/3.),iqt.Y)

    References
    ----------
    .. [1] Neutron Spin Echo Investigations on the Segmental Dynamics of Polymers in Melts, Networks and Solutions
           in Neutron Spin Echo Spectroscopy Viscoelasticity Rheology
           Volume 134 of the series Advances in Polymer Science pp 1-129
           DOI 10.1007/3-540-68449-2_1

    """
    quad=scipy.integrate.quad
    kb=1.3806503e-23
    tt=np.r_[t]*1e-9
    tt[t==0]=1e-20 # avoid zero
    # Zimm diffusion coefficient
    OmegaZ=(q*1e9)**3*kb*Temp/(6*pi*viscosity)

    _g_integrand=lambda x,y:math.cos(y*x)/x/x*(1-math.exp(-x**(3./2.)/math.sqrt(2)))
    _g=lambda y:2./pi*quad(_g_integrand,0,np.inf,args=(y,),epsrel=rtol,epsabs=tol,limit=limit)[0]

    _z_integrand=lambda u,t:math.exp(-u-(OmegaZ*t)**(2./3.)*_g(u*(OmegaZ*t)**(2./3.)))

    y1=[ quad(_z_integrand,0,np.inf,args=(ttt),epsrel=rtol,epsabs=tol,limit=limit)[0] for ttt in tt]

    result=dA(np.c_[t,amp*np.r_[y1]].T)
    result.setColumnIndex(iey=None)
    result.columnname='t;Iqt'
    result.q=q
    result.OmegaZimm=OmegaZ
    result.Temperature=Temp
    result.viscosity=viscosity
    result.amplitude=amp
    return result

def resolution(t, s0=1, m0=0, s1=None, m1=None, s2=None, m2=None, s3=None, m3=None, s4=None, m4=None, s5=None, m5=None,
                 a0=1, a1=1, a2=1, a3=1, a4=1, a5=1, bgr=0, resolution_w=None):
    r"""
    Resolution in time domain as multiple Gaussians for inelastic measurement as backscattering or time of flight instruement.

    Multiple Gaussians define the function to describe a resolution measurement.
    Use resolution_w to fit with the appropriate normalized Gaussians.
    See Notes

    Parameters
    ----------
    t : array
        Times
    s0,s1,... : float
        Width of Gaussian functions representing a resolution measurement.
        The number of si not None determines the number of Gaussians.
    m0, m1,.... : float, None
        Means of the Gaussian functions representing a resolution measurement.
    a0, a1,.... : float, None
        Amplitudes of the Gaussian functions representing a resolution measurement.
    bgr : float, default=0
        Background
    resolution_w : dataArray
        Resolution in w domain with attributes sigmas, amps which are used instead of si, ai.
        This represents the Fourier transform of multi gauss resolution from w to t domain.
        The m0..m5 are NOT used as these result only in a phase shift.

    Returns
    -------
        dataArray

    Notes
    -----
    In a typical inelastic experiment the resolution is measured by e.g. a vanadium meausrement (elastic scatterer).
    This is described in w domain by a multi Gaussian function as in resw=resolution_w(w,...) with
    amplitudes ai_w, width si_w and common mean m_w.
    resolution(t,resolution_w=resw) defines the Fourier transform of resolution_w using the same coefficients.
    mi_t are set by default to zero as mi_w lead only to a phase shift. It is easiest to shift w values in w domain as it
    corresponds to a shift of the elastic line.

    The used Gaussians are normalized that they are a pair of Fourier transforms:

    .. math:: R_t(t,m_i,s_i,a_i)=\sum_i a_i s_i e^{-\frac{1}{2}s_i^2 t^2} \Leftrightarrow  R_w(w,m_i,s_i,a_i)=\sum_i a_i e^{-\frac{1}{2}(\frac{w-m_i}{s_i})^2}

    under the Fourier transform defined as

    .. math:: F(f(t)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt

    .. math:: F(f(w)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(\omega) e^{i\omega t} d\omega


    Examples
    --------
    ::

     import jscatter as js
     resw=js.dynamic.resolution_w(w, s0=12, m0=0, a0=2) # resolution in w domain
     # representing the fouriertransform of resw as a gaussian transfoms to ag gaussian
     rest=js.dynamic.resolution(t,resolution=resw)

    """
    gauss=lambda x,mean,sigma:sigma*np.exp(-0.5*((x-mean)/sigma)**2)
    if resolution is None:
        means = [m0,m1,m2,m3,m4,m5]
        sigmas= [s0,s1,s2,s3,s4,s5]
        amps  = [a0,a1,a2,a3,a4,a5]
    else:
        means  = [m0,m1,m2,m3,m4,m5]
        sigmas = 1./np.array(resolution.sigmas)
        amps   = np.array(resolution.amps)
    w=np.atleast_1d(w)
    Y=np.r_[[a*_gauss(t, m, s) for s,m,a in zip(sigmas,means,amps) if (s is not None) & (m is not None)]].sum(axis=0)
    result=dA(np.c_[t,Y+bgr].T)
    result.setColumnIndex(iey=None)
    result.columnname = 't;Rqt'
    result.means = means
    result.sigmas= sigmas
    result.amps  = amps
    return result

##################################################################
# frequenxy domain                                               #
##################################################################

def getHWHM(data,center=0,gap=0):
    """
    Find half width at half maximum of a distribution around zero.

    The hwhm is determined from cubicspline between Y values to find Y.max/2.
    Requirement Y.max/2>Y.min and increasing X values.
    If nothing is found an empty list is returned

    Parameters
    ----------
    data : dataArray
        Distribution
    center: float, default=0
        Center (symmetry point) of data.
        If None the position of the maximum is used.
    gap : float, default 0
        Exclude values around center as it may contain a singularity.
        Excludes values within X<= abs(center-gap).

    Returns
    -------
        list of float with hwhm X>0 , X<0 if existing


    """
    gap=abs(gap)
    if center is None:
        # determine center
        center=data.X[data.Y.argmax()]
    data1 = data[:, data.X >= center+gap]
    data2 = data[:, data.X <= center-gap]
    data1.X = data1.X - center
    data2.X = data2.X - center
    res=[]
    try:
        max=data1.Y.max()
        min = data1.Y.min()
        if min < max/2. and np.all(np.diff(data1.X) > 0):
            #hwhm1=scipy.interpolate.interp1d(data1.Y.astype(float)[::-1],data1.X.astype(float)[::-1], kind=2)((max-min) / 2.)
            hwhm1=np.interp((max-min)/ 2., data1.Y.astype(float)[::-1], data1.X.astype(float)[::-1])
            res.append(np.abs(hwhm1))
    except:res.append(None)
    try:
        max = data2.Y.max()
        min = data2.Y.min()
        if min < max/2. and np.all(np.diff(data2.X) > 0):
            #hwhm2=scipy.interpolate.interp1d(data1.Y.astype(float),data1.X.astype(float), kind=2)((max-min)/ 2.)
            hwhm2=np.interp((max-min)/ 2., data2.Y.astype(float), data2.X.astype(float))
            res.append(np.abs(hwhm2))
    except:res.append(None)
    return res

def elastic_w(w):
    """
    Elastic line; dynamic structure factor in w domain.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    w0 : float
        Position of elastic line :math:`\delta(w=w0)=1`

    Returns
    -------
        dataArray

    """
    Iqw=np.zeros_like(w)
    Iqw[np.abs(w)<1e-8]=1.
    result=dA(np.c_[w,Iqw].T)
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    result.modelname=sys._getframe().f_code.co_name
    return result

def transDiff_w(w, q, D):
    """
    Translational diffusion; dynamic structure factor in w domain.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    D : float
        Diffusion constant in nm**2/ns

    Returns
    -------
         dataArray

    References
    ----------
    .. [0] Scattering of Slow Neutrons by a Liquid
           Vineyard G Physical Review 1958 vol: 110 (5) pp: 999-1010

    """
    dw= q * q * D
    res=1/pi*dw/(dw*dw+w*w)
    result=dA(np.c_[w,res].T)
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    result.modelname=sys._getframe().f_code.co_name
    result.wavevector = q
    result.D = D
    return result

def jumpDiff_w(w,q,t0,r0):
    """
    Jump diffusion; dynamic structure factor in w domain.

    Jump diffusion as a markovian random walk. Jump length distribution is a Gaussian
    with width r0 and jump rate distribution with width G (Poisson).
    Diffusion coefficient D=r0**2/2t0.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    t0 : float
        Mean residence time in a Poisson distribution of jump times. In units ns.
        G = 1/tg = Mean jump rate
    r0 : float
        Root mean square jump length in 3 dimensions <r**2> = 3*r_0**2


    Returns
    -------
         dataArray

    References
    ----------
    .. [1] Incoherent neutron scattering functions for random jump diffusion in bounded and infinite media.
           Hall, P. L. & Ross, D. K. Mol. Phys. 42, 637–682 (1981).

    """
    Ln = lambda w, dw: dw /( dw*dw + w * w )/pi
    dw=1./t0*(1-np.exp(-q**2*r0**2/2.))
    result=dA(np.c_[w,Ln(w,dw)].T)
    result.modelname=sys._getframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    result.wavevector=q
    result.meanresidencetime=t0
    result.meanjumplength=r0
    return result

_erfi=special.erfi
_G=special.gamma
_h1f1=special.hyp1f1
_erf=special.erf
_Gi=special.gammainc

def diffusionHarmonicPotential_w(w, q, tau, rmsd, ndim=3,nmax='auto'):
    """
    Diffusion in a harmonic potential for dimension 1,2,3 (isotropic averaged), dynamic structure factor in w domain.

    An approach worked out by Volino et al [1]_ assuming Gaussian confinement and leads to a more efficient 
    formulation by replacing the expression for diffusion in a sphere with a simpler expression pertaining 
    to a soft confinement in harmonic potential. Ds = ⟨u**2⟩/t0

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    tau : float
        Mean correlation time time. In units ns.
    rmsd : float
        Root mean square displacement (width) of the Gaussian in units nm.
    ndim : 1,2,3, default=3
        Dimensionality of the potential.
    nmax : int,'auto'
        Order of expansion.
        'auto' -> nmax = min(max(int(6*q * q * u2),30),1000)

    Returns
    -------
         dataArray

    Notes
    -----
    Volino et al [1]_ compared the behaviour of this approach to the well known expression for diffusion in a sphere. 
    Even if the details differ, the salient features of both models match if the radius R**2 ≃ 5*u0**2 and
    the diffusion constant inside the sphere relates to the relaxation time of particle correlation t0= ⟨u**2⟩/Ds
    towards the Gaussian with width u0=⟨u**2⟩**0.5.

    ndim=3
     Here we use the Fourier transform of equ 23 with equ. 29a+b in [1]_.
     For order n larger 30 the Stirling approximation for n! in equ 27b of [1]_ is used.
    ndim=2
     Here we use the Fourier transform of equ 23 with equ. 28a+b in [1]_.
    ndim=1
     The equation given by Violino seems to be wrong !!!!
     Dont use this !!!!!!!!
     Use the model from time domain and use FFT as in example given
     Here we use the Fourier transform of equ 23 with equ. 29a+b in [1]_.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100]
     ql=np.r_[1:14.1:1.3]
     p=js.grace()
     iqt3=js.dL([js.dynamic.gaussDiffusion3D_w(w=w,q=q,t0=0.14,u0=0.34,ndim=3) for q in ql])
     iqt2=js.dL([js.dynamic.gaussDiffusion3D_w(w=w,q=q,t0=0.14,u0=0.34,ndim=2) for q in ql])
     # as ndim=1 is a wrong solution use this instead
     iqt1=js.dL([js.dynamic.time2frequencyFF(js.dynamic.diffusionHarmonicPotential,'elastic',w=np.r_[-100:100:0.01],dw=0,q=q, rmsd=u0, tau=t0 ,ndim=1) for q in ql])
     p.plot(iqt2)
     p.plot(iqt3)


    References
    ----------
    .. [1] Gaussian model for localized translational motion: Application to incoherent neutron scattering. 
           Volino, F., Perrin, J. C. & Lyonnard, S. J. Phys. Chem. B 110, 11217–11223 (2006).

    """
    w=np.array(w,float)
    u2= rmsd ** 2
    if not isinstance(nmax,int):
        nmax = min(max(int(6*q * q * u2),30),1000)
    Ln = lambda w, t0, n: t0 / pi * n / (n * n + w * w * t0 * t0)        # equ 25a

    if ndim==3:
        # 3D case
        A0=lambda q:np.exp(-q*q*u2)                                        # EISF  equ 27a
        def An(q,n):
            s=(n<30) # select not to large n and use for the other the Stirling equation
            An=np.r_[ (q*q*u2)**n[s]/factorial(n[s]) , (q*q*u2/n[~s]*np.e)**n[~s]/ (2*pi*n[~s])**0.5      ]
            An*=np.exp(-q*q*u2)
            return An

        n=np.r_[:nmax]+1
        an=An(q,n)
        sel=np.isfinite(an)       # remove An with inf or nan
        Iqw=(an[sel,None] * Ln(w, tau, n[sel, None])).sum(axis=0)          # equ 23 after ft
        Iqw[np.abs(w)<1e-8]+=A0(q)

    elif ndim==2:
        # 2D case
        A0=lambda q:  pi**0.5/2.*np.exp(-q*q*u2)*_erfi((q*q*u2)**0.5)/(q*q*u2)**0.5          # EISF  equ 28a
        An=lambda q,n:pi**0.5/2.* (q*q*u2)**n * _h1f1(1+n,1.5+n,-q*q*u2)  / _G(1.5+n)        # equ 28b
        n=np.r_[:nmax]+1
        Iqw=(An(q,n)[:,None] * Ln(w, tau, n[:, None])).sum(axis=0)                              # equ 23 after ft
        Iqw[np.abs(w)<1e-8]+=A0(q)

    elif ndim==1:
        print(' THis seems to be wrong as given in the paper')
        # 1D case
        A0=lambda q:pi**0.5/2.*_erf((q*q*u2)**0.5)/(q*q*u2)**0.5                       # EISF  equ 29a
        An=lambda q,n:( _G(0.5+n)-_Gi(0.5+n,q*q*u2) ) / (2*(q*q*u2)**0.5*_G(1+n))           # equ 29b
        n=np.r_[:nmax]+1
        an=An(q,n)
        sel=np.isfinite(an)       # remove An with inf or nan
        Iqw=(an[sel,None] * Ln(w, tau, n[sel, None])).sum(axis=0)                        # equ 23 after ft
        Iqw[np.abs(w)<1e-8]+=A0(q)
    else:
        raise Exception('ndim should be one of 1,2,3 ')

    result=dA(np.c_[w, Iqw].T)
    result.modelname=sys._getframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    result.u0=rmsd
    result.dimension=ndim
    result.wavevector=q
    result.meancorrelationtime=tau
    result.gaussWidth=rmsd
    result.nmax=nmax
    result.Ds = rmsd ** 2 / tau
    return result

#: First 99 coefficients from Volino for diffusionInSphere_w
# VolinoCoefficient=np.loadtxt(_path_+'/VolinoCoefficients.dat')  # numpy cannot load because of utf8
with open(_path_+'/VolinoCoefficients.dat') as f:VolinoC = f.readlines()
VolinoCoefficient=np.array([  line.strip().split() for line in VolinoC if line[0]!='#'],dtype=float)

def diffusionInSphere_w(w,q,D,R):
    """
    Diffusion inside of a sphere; dynamic structure factor in w domain.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    D : float
        Diffusion coefficient in units nm**2/ns
    R : float
        Radius of the sphere in units nm.

    Returns
    -------
         dataArray

    Notes
    -----
    Here we use equ 33 in [1]_ with the first 99 solutions of equ 27 a+b as given in [1]_.
    This is valid for q*R<20 with accuracy of ~0.001 as given in [1]_.
    If we look at a comparison with free diffusion the valid range seems to be smaller.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100]
     ql=np.r_[1:14.1:1.3]
     p=js.grace()
     iqw=js.dL([js.dynamic.diffusionInSphere_w(w=w,q=q,D=0.14,R=0.2) for q in ql])
     p.plot(iqw)
     p.yaxis(scale='l')

    Compare different kinds of diffusion in restricted geometry.
    ::

     import jscatter as js
     import numpy as np
     # compare the HWHM
     ql=np.r_[0.5:15.:0.2]
     D=0.1;R=0.5
     w=np.r_[-js.loglist(0.01,100,100)[::-1],0,js.loglist(0.01,100,100)]
     iqwS=js.dL([js.dynamic.diffusionInSphere_w(w=w,q=q,D=D,R=R) for q in ql])
     iqwD=js.dL([js.dynamic.transDiff_w(w=w,q=q,D=D) for q in ql[:]])
     u0=R/4.33**0.5;t0=R**2/4.33/D
     iqwG3=js.dL([js.dynamic.gaussDiffusion3D_w(w=w,q=q,u0=u0,t0=t0) for q in ql])
     iqwG2=js.dL([js.dynamic.gaussDiffusion2D_w(w=w,q=q,u0=u0,t0=t0) for q in ql])
     p1=js.grace()
     p1.subtitle('Comparison of HWHM for different types of diffusion')
     p1.plot((R*iqwD.wavevector.array)**2,[js.dynamic.getHWHM(dat)[0]/(D/R**2) for dat in iqwD], le='free diffusion')
     p1.plot((R*iqwS.wavevector.array)**2,[js.dynamic.getHWHM(dat)[0]/(D/R**2) for dat in iqwS], le='diffusion in sphere')
     p1.plot([0.1,60],[4.33296]*2,li=[1,1,1])
     p1.plot((R*iqwG3.wavevector.array)**2,[js.dynamic.getHWHM(dat)[0]/(D/R**2) for dat in iqwG3], le='diffusion 3D Gauss')
     p1.plot((R*iqwG2.wavevector.array)**2,[js.dynamic.getHWHM(dat)[0]/(D/R**2) for dat in iqwG2], le='diffusion 2D Gauss')
     r0=.5;t0=r0**2/2./D
     iqwJ=js.dL([js.dynamic.jumpDiff_w(w=w,q=q,r0=r0,t0=t0) for q in ql])
     ii=54;p1.plot((r0*iqwJ.wavevector.array[:ii])**2,[js.dynamic.getHWHM(dat)[0]/(D/r0**2) for dat in iqwJ[:ii]], le='jump diffusion')
     p1.yaxis(min=0.1,max=100,scale='l',label='HWHM/(D/R**2)')
     p1.xaxis(min=0.1,max=100,scale='l',label='(Q*R)\S2')
     p1.legend(x=0.2,y=50)

    References
    ----------
    .. [1] Neutron incoherent scattering law for diffusion in a potential of spherical symmetry:
           general formalism and application to diffusion inside a sphere.
           Volino, F. & Dianoux, A. J.,  Mol. Phys. 41, 271–279 (1980).

    """
    qR=q*R
    x=VolinoCoefficient[1:50,0]         # x_n_l
    x2=x**2
    l=VolinoCoefficient[1:50,1].astype(int)
    n=VolinoCoefficient[1:50,2].astype(int)
    w=np.array(w,float)

    Ln=lambda w,g:  g/(g*g+w*w)
    A0=lambda qa: (3*spjn(1,qa)/qa)**2
    def Anl(qa):
        # equ 31 a+b in [1]_
        res=np.zeros_like(x)
        s= (x==qa)
        if np.any(s):
            res[s]=1.5*spjn(l[s],x[s])**2*(x2[s]-l[s]*(l[s]+1))/x2[s]
        if np.any(~s):
            s=~s  # not s
            res[s] = 6*x2[s]/(x2[s]-l[s]*(l[s]+1)) * ((qa*spjn(l[s]+1,qa)-l[s]*spjn(l[s],qa)) / (qa**2-x2[s]))**2
        return res

    Iqw=1/pi*(  ((2*l+1)*Anl(qR))[:,None]*Ln(w,x2[:,None]*D/R**2)          ).sum(axis=0)   # equ 33
    Iqw[np.abs(w)<1e-8]+=A0(q)

    result=dA(np.c_[w,Iqw].T)
    result.modelname=sys._getframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    result.radius=R
    result.wavevector=q
    result.diffusion=D
    return result

def rotDiffusion_w(w,q,cloud,Dr,lmax='auto'):
    """
    Rotational diffusion of an object (dummy atoms); dynamic structure factor in w domain.

    A cloud of dummy atoms can be used for coarse graining of a nonspherical object e.g. for amino acids in proteins.
    On the other hand its just a way to integrate over an object e.g. a sphere or ellipsoid.
    We use [2]_ for an objekt of arbitrary shape modified for incoherent scattering.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in units 1/nm
    cloud : array Nx3 or Nx4 or float
        - A cloud of N dummy atoms with positions cloud[:3] that describe an object.
        - If given, cloud[3] is the incoherent scattering length :math:`b_{inc}`.
        - If cloud[3] not given :math:`b_{inc}=1/N` that :math:`\sum_{1..N}b_{inc,N}=1`.
        - If cloud is single float the value is used as radius of a sphere with 10x10x10 grid.
    Dr : float
        Rotational diffusion constant in units 1/ns.
    lmax : int
        Maximum order of spherical bessel function.
        'auto' -> lmax > pi*r.max()*q/6.

    Returns
    -------
        dataArray

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     R=2;NN=5
     grid= np.mgrid[-R:R:1j*NN, -R:R:1j*NN,-R:R:1j*NN].reshape(3,-1).T
     # points inside of sphere with radius R
     p2=1*2 # p defines a superball with 1->sphere p=inf cuboid ....
     inside=lambda xyz,R:(np.abs(xyz[:,0])/R)**p2+(np.abs(xyz[:,1])/R)**p2+(np.abs(xyz[:,2])/R)**p2<=1
     insidegrid=grid[inside(grid,R)]
     Drot=js.formel.Drot(R)
     ql=np.r_[0.5:15.:2]
     w=np.r_[-100:100:0.1]
     p=js.grace()
     iqwR=js.dL([js.dynamic.rotDiffusion_w(w,q,insidegrid,Drot) for q in ql])
     p.plot(iqwR,le='NN=%.1g q=$wavevector nm\S-1' %(NN))
     iqwR=js.dL([js.dynamic.rotDiffusion_w(w,q,2,Drot) for q in ql])
     p.plot(iqwR,li=1,sy=0,le='NN=10 $wavevector nm\S-1')
     p.yaxis(min=-0.001,max=0.001,scale='n')
     p.legend()

    References
    ----------
    .. [1] Incoherent scattering law for neutron quasi-elastic scattering in liquid crystals.
           Dianoux, A., Volino, F. & Hervet, H. Mol. Phys. 30, 37–41 (1975).
    .. [2] Effect of rotational diffusion on quasielastic light scattering from fractal colloid aggregates.
           Lindsay, H., Klein, R., Weitz, D., Lin, M. & Meakin, P. Phys. Rev. A 38, 2614–2626 (1988).

    """
    Ylm = special.sph_harm
    #: Lorentzian
    Ln=lambda w,g:  g/(g*g+w*w)/pi
    if isinstance(cloud,(float,int)):
        R=cloud
        NN=10
        grid= np.mgrid[-R:R:1j*NN, -R:R:1j*NN,-R:R:1j*NN].reshape(3,-1).T
        inside=lambda xyz,R:(np.abs(xyz[:,0])/R)**2+(np.abs(xyz[:,1])/R)**2+(np.abs(xyz[:,2])/R)**2<=1
        cloud=grid[inside(grid,R)]
    if cloud.shape[1]==4:
        # last column is scattering length
        blength=cloud[:,3]
        cloud=cloud[:,:3]
    else:
        blength=np.ones(cloud.shape[0])
    w = np.array(w, float)
    bl2 = blength ** 2
    r,p,t=np.r_[[formel.xyz2rphitheta(r) for r in cloud]].T
    pp=p[:,None]
    tt=t[:,None]
    qr=q*r
    if not isinstance(lmax,int):
        # lmax = pi * r.max() * q  / 6. # a la Cryson
        lmax = min(max(int(pi*qr.max()/6.),7),100)

    # coh is sum over i then squared and sum over m    see Lindsay equ 19
    #bjlylm = [((bl*spjn(l,q*r)[0]*Ylm(np.r_[-l:l+1],l,pp,tt]).T).sum(axis=0)**2).sum() for l in np.r_[:lmax+1]]
    # incoherent with i=j ->  Sum_m(Ylm) leads to (2l+1)/4pi
    bjlylm=[(bl2*spjn(l,qr)**2*(2*l+1)).sum()   for l in np.r_[:lmax + 1]]
    # add Lorentzian
    Iqw= np.c_[[bjlylm[l].real * Ln(w,l*(l+1)*Dr) for l in np.r_[:lmax+1]]].sum(axis=0)
    result=dA(np.c_[w,Iqw].T)
    result.modelname=sys._getframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    result.radiusOfGyration=np.sum(r**2)**0.5
    result.wavevector=q
    result.rotDiffusion=Dr
    result.lmax=lmax
    return result

def nSiteJumpDiffusion_w(w,q,N,t0,r0):
    """
    Random walk among N equidistant sites (isotropic averaged); dynamic structure factor in w domain.

    E.g. for CH3 group rotational jump diffusion over 3 sites.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q: float
        Wavevector in units 1/nm
    N : int
        Number of jump sites, jump angle 2pi/N
    r0 : float
        Distance of sites from center of rotation.
        For CH3 eg 0.12 nm.
    t0 : float
        Rotational correlation time.

    Returns
    -------
        dataArray

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100]
     ql=np.r_[1:14.1:1.3]
     p=js.grace()
     iqw=js.dL([js.dynamic.nSiteJumpDiffusion_w(w=w,q=q,N=3,t0=0.001,r0=0.12) for q in ql])
     p.plot(iqw)

    References
    ----------
    .. [1] Incoherent scattering law for neutron quasi-elastic scattering in liquid crystals.
           Dianoux, A., Volino, F. & Hervet, H., Mol. Phys. 30, 37–41 (1975).

    """
    w=np.array(w,float)
    #: Lorentzian
    Ln=lambda w,tn:  tn/(1+(w*tn)**2)/pi
    def Bn(qa,n):
        return  np.sum([spjn(0,2*qa*np.sin(pi*p/N))*np.cos(n*2*pi*p/N) for p in np.r_[:N]+1 ])/N
    B0=np.sum([spjn(0,2*q*r0*np.sin(pi*p/N)) for p in np.r_[:N]+1])/N
    t1=t0/(1-np.cos(2*pi/N))
    tn=lambda n:t1*np.sin(pi/N)**2/np.sin(n*pi/N)**2

    Iqw= np.c_[[ Bn(q*r0,n) * Ln(w,tn(n)) for n in np.r_[1:N] ]].sum(axis=0)
    Iqw[np.abs(w)<1e-8]+=B0
    result=dA(np.c_[w,Iqw].T)
    result.modelname=sys._getframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    result.r0=r0
    result.wavevector=q
    result.t0=t0
    result.N=N
    return result

def resolution_w(w, s0=1, m0=0, s1=None, m1=None, s2=None, m2=None, s3=None, m3=None, s4=None, m4=None, s5=None, m5=None,
                 a0=1, a1=1, a2=1, a3=1, a4=1, a5=1, bgr=0, resolution=None):
    r"""
    Resolution as multiple Gaussians for inelastic measurement as backscattering or time of flight instruement in w domain.

    Multiple Gaussians define the function to describe a resolution measurement.
    Use only a common mi to account for a shift.
    See resolution for transform to time domain.

    Parameters
    ----------
    w : array
        Frequencies
    s0,s1,... : float
        Sigmas of several Gaussian functions representing a resolution measurement.
        The number of si not none determines the number of Gaussians.
    m0, m1,.... : float, None
        Means of the Gaussian functions representing a resolution measurement.
    a0, a1,.... : float, None
        Amplitudes of the Gaussian functions representing a resolution measurement.
    bgr : float, default=0
        Background
    resolution : dataArray
        Resolution in t space with attributes means, sigmas, amps which are used instead of si, mi, ai.
        This represents the fourier transform of multi gauss resolution from t to w space.
        The mi are used as mi from resolution_w result in a phase shift.

    Returns
    -------
        dataArray
            .means
            .amps
            .sigmas

    Notes
    -----
    In a typical inelastic experiment the resolution is measured by e.g. a vanadium meausrement (elastic scatterer).
    This is described in w domain by a multi Gaussian function as in resw=resolution_w(w,...) with
    amplitudes ai_w, width si_w and common mean m_w.
    resolution(t,resolution_w=resw) defines the Fourier transform of resolution_w using the same coefficients.
    mi_t are set by default to zero as mi_w lead only to a phase shift. It is easiest to shift w values in w domain as it
    corresponds to a shift of the elastic line.

    The used Gaussians are normalized that they are a pair of Fourier transforms:

    .. math:: R_t(t,m_i,s_i,a_i)=\sum_i a_i s_i e^{-\frac{1}{2}s_i^2 t^2} \Leftrightarrow  R_w(w,m_i,s_i,a_i)=\sum_i a_i e^{-\frac{1}{2}(\frac{w-m_i}{s_i})^2}

    under the Fourier transform  defined as

    .. math:: F(f(t)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt

    .. math:: F(f(w)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(\omega) e^{i\omega t} d\omega


    Examples
    --------
    ::

     import jscatter as js
     # read data
     vana=js.dL('vana_0p2mm.scat') # use your files here
     start={'s0':0.5,'m0':0,'a0':1,'bgr':0.0073}
     dm=5
     vana[0].setlimit(m0=[-dm,dm],m1=[-dm,dm],m2=[-dm,dm],m3=[-dm,dm],m4=[-dm,dm],m5=[-dm,dm])
     vana[0].fit(js.dynamic.resolution_w,start,{},{'w':'X'})


    """
    gauss=lambda x,mean,sigma:np.exp(-0.5*((x-mean)/sigma)**2)

    if resolution is None:
        means = [m0,m1,m2,m3,m4,m5]
        sigmas= [s0,s1,s2,s3,s4,s5]
        amps  = [a0,a1,a2,a3,a4,a5]
    else:
        means  = [m0,m1,m2,m3,m4,m5]
        sigmas = 1./np.array(resolution.sigmas)
        amps   = np.array(resolution.amps)
    w=np.atleast_1d(w)
    if isinstance(resolution,str): # elastic
        Y = np.zeros_like(w)
        Y[np.abs(w - m0) < 1e-8] = 1.
        integral=1
    else:
        Y=np.r_[[a*gauss(w, m, s) for s,m,a in zip(sigmas,means,amps) if (s is not None) & (m is not None)]].sum(axis=0)
        integral=np.trapz(Y,w)
    result=dA(np.c_[w,Y+bgr].T)
    result.setColumnIndex(iey=None)
    result.columnname='w;Rw'
    result.means = means
    result.sigmas= sigmas
    result.amps  = amps
    result.integral=integral
    return result

def time2frequencyFF(timemodel,resolution,w=None,tfactor=7,**kwargs):
    r"""
    Fast Fourier transform from time domain to frequency domain for inelastic neutron scattering.

    Shortcut t2fFF calls this function.

    Parameters
    ----------
    timemodel : function, None
        Model for I(q,t) in time domain. t in units of ns.
        If None a constant function equal one is used like elastic scattering to fit resolution measurement.
    resolution : dataArray
        dataArray that describes the resolution function from a fit with resolution_w or parametrized.
        A nonzero bgr in resolution is ignored and needs to be added afterwards.
        Resolution width are in the range of 6 1/ns (IN5 TOF) or 1 1/ns (Spheres BS).
    w : array
        Frequencies for the result, e.g. from experimental data.
        If w is None the frequencies w of the resolution are used.
        This allows to use the fit of a resolution to be used with same w values.
    kwargs : keyword args
        Additional keyword arguments that are passed to timemodel.
    tfactor : float, default 7
        Factor to determine max time for timemodel.
        tmax=1/(min(resolution_width)*tfactor) determines the resolution to decay as :math:`e^{-tfactor^2/2}`.
        THe timestep is dt=1/max(|w|). A minimum of len(w) steps is used (which might increase tmax).
        Increase tfactor if artefacts (wobbling) from the limited timewindow are visible as the limited timeintervall
        acts like a window function for the Fourier transform.

    Returns
    -------
    dataArray : A symmetric spectrum is returned.
     .Sq     :math:`\rightarrow S(q)=\int_{-\omega_{min}}^{\omega_{max}}S(Q,\omega)d\omega\approx\int_{-\infty}^{\infty} S(Q,\omega)d\omega = I(q,t=0)`
             Integration is done by a cubic spline in w domain on the 'raw' fourier transfom of timemodel.

     .Iqt    timemodel(t,kwargs) dataarray returned from timemodel.
             Implicitly this is the Fourier transform to timedomain after a succesfull fit in w domain.
             Using a heuristic model in timedomain as multiple Gaussians or stretched exponentials allows a convenient
             transform to timedomain of experimental data.


    Notes
    -----
    We use Fourier transform with real signals. The transform is defined as

    .. math:: F(f(t)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt

    .. math:: F(f(w)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(\omega) e^{i\omega t} d\omega

    The resolution function is defined as (see resolution_w)

    .. math:: R_w(w,m_i,s_i,a_i)&=\sum_i a_i e^{-\frac{1}{2}(\frac{w-m_i}{s_i})^2} \\

                &=\frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} \sum_i{a_i s_i e^{-\frac{1}{2}s_i^2t^2}} e^{-i\omega t} dt

    using the resolution in timedomain :math:`R_t(t,m_i,s_i,a_i)=\sum_i a_i s_i e^{-\frac{1}{2}s_i^2 t^2}`

    The Fourier tranform of the timemodel I(q,t) is

    .. math:: I(q,w) = \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} R_t(t,m_i,s_i,a_i) I(q,t) e^{-i\omega t} dt

    The integral is calculated by fast Fourier transform as

    .. math:: I(q,m\Delta w) = \frac{1}{\sqrt{2\pi}} \Delta t \sum_{n=-N}^{N} R_t(n\Delta t,...) I(q,n\Delta t) e^{-i mn/N}

    with :math:`t_{max}=tfactor/min(s_i)` large enough that the resolution decayed to be negligible.
    Actually the resolution acts like a window function to reduce spectral leakage with vanishing values at :math:`t_{max}` .
    Nevertheless, due to the cutoff at :math:`t_{max}` a wobbling migth appear indicating that :math:`t_{max}` needs to be larger.

    **Mixed domain models**
    Associativity and Convolution theorem allow to mix models from frequency domain and time domain.
    Fourier transform needs the resolution included in time domain as it acts like a window function.
    After tranformation to frequency domain the w domain models have to be convoluted with FFT transformed model.
    Resolution is already taken into account in this way.

    Examples
    --------
    Other usage example with a comparison of w domain and transfomed from time domain can be found in
    :ref:`A comparison of different dynamic models in frequency domain` .

    Compare transDiffusion transform from time domain with direct convolution in w domain.
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100:0.5]
     start={'s0':6,'m0':0,'a0':1,'s1':None,'m1':0,'a1':1,'bgr':0.00}
     resolution=js.dynamic.resolution_w(w,**start)
     p=js.grace()
     D=0.035;qq=3  # diffusion coefficient of protein alcohol dehydrogenase (140 kDa) is 0.035 nm**2/ns
     p.title('Inelastic spectrum IN5 like')
     p.subtitle('resolution width about 6 ns\S-1\N, Q=%.2g nm\S-1\N' %(qq))
     # compare diffusion with convolution and transform from timedomain
     diff_ffw=js.dynamic.time2frequencyFF(js.dynamic.simpleDiffusion,resolution,q=qq,D=D)
     diff_w=js.dynamic.transDiff_w(w, q=qq, D=D)
     p.plot(diff_w,sy=0,li=[1,3,3],le='original diffusion D=%.3g nm\S2\N/ns' %(D))
     p.plot(diff_ffw,sy=[2,0.3,2],le='transform from time domain')
     p.plot(diff_ffw.X,diff_ffw.Y+diff_ffw.Y.max()*1e-3,sy=[2,0.3,7],le='transform from time domain with 10\S-3\N bgr')
     # resolution has to be normalized in convolve
     diff_cw=js.dynamic.convolve(diff_w,resolution,normB=1)
     p.plot(diff_cw,sy=0,li=[1,3,4],le='after convolution in w domain')
     p.plot(resolution.X,resolution.Y/resolution.integral,sy=0,li=[1,1,1],le='resolution')
     p.yaxis(min=1e-6,max=5,scale='l',label='S(Q,w)')
     p.xaxis(min=-100,max=100,label='w / ns\S-1')
     p.legend()
     p.text(string=r'convolution edge ==>\nmake broader and cut',x=10,y=8e-6)

    Compare the resolutions direct and from transform from time domain.
    ::

     p=js.grace()
     fwres=js.dynamic.time2frequencyFF(None,resolution)
     p.plot(fwres,le='fft only resolution')
     p.plot(resolution,sy=0,li=2,le='original resolution')

    """
    # prerequisites
    if w is None:  w=resolution.X
    if timemodel is None:
        timemodel=lambda t,**kwargs:dA(np.c_[t,np.ones_like(t)].T)
    gauss = lambda t, si: si*np.exp(-0.5 * (si * t)**2 )

    # filter for given values (remove None) and drop bgr in resolution
    if isinstance(resolution,str):
        si=np.r_[0.5]
    else:
        sma=np.r_[[[si,mi,ai] for si, mi, ai in
                        zip(resolution.sigmas,resolution.means,resolution.amps) if (si is not None) & (mi is not None)]]
        si=sma[:,0,None]
        mi=sma[:,1,None]    # ignored
        ai=sma[:,2,None]

    # determine the times and differences dt
    dt=1./np.max(np.abs(w))
    nn=int(np.max(w)/si.min()*tfactor)
    nn=max(nn,len(w))
    tt=np.r_[0:nn]*dt

    # calc values
    if isinstance(resolution,str):
        timeresol=np.ones_like(tt)
    else:
        timeresol=(ai*gauss(tt,si)).sum(axis=0)         # resolution normalized to timeresol(w=0)=1
        timeresol/=(timeresol[0] )                      # That  S(Q)= integral[-w_min,w_max] S(Q,w)= = I(Q, t=0)
    kwargs.update(t=tt)
    tm=timemodel(**kwargs)
    RY=timeresol*tm.Y               # resolution * timemodel
    # make it symmetric zero only once
    RY=np.r_[RY[:0:-1],RY]
    # do rfft from -N to N
    # using spectrum from -N,N the shift theorem says we get a
    # exp[-j*2*pi*f*N/2] phase leading to alternating sign => use the absolute value
    wn = 2*pi*np.fft.rfftfreq(2*nn-1, dt)               # frequencies
    wY = dt * np.abs(np.fft.rfft(RY).real)/(2*pi)       # fft

    # now try to average or interpolate for needed w values
    wn=np.r_[-wn[:0:-1],wn]
    wY=np.r_[wY[:0:-1],wY]
    integral=scipy.integrate.simps(wY, wn)

    result=dA(np.c_[wn,wY].T)
    result.setattr(tm)
    try:
        result.modelname=result.modelname+'_t2w'
    except:
        result.modelname = '_t2w'
    result.Sq=integral
    result.Iqt=tm
    result.timeresol=timeresol
    result.setColumnIndex(iey=None)
    result.columnname='w;Iqw'
    return result

t2fFF=time2frequencyFF

def shiftAndBinning(data, w=None, dw=None, w0=0):
    """
    Shift spectrum and average (binning) in intervals.

    The intention is to shift spectra and average over intervalls.
    It should be used after convolution with the instrument resolution, when singular values
    at zero are smeared by resolution.

    Parameters
    ----------
    data : dataArray
        Data (from model) to be shifted and averaged in intervals to meet experimental data.
    w : array
        New X values (e.g. from experiment). If w is None data.X values are used.
    w0 : float
        Shift by w0 that wnew=wold+w0
    dw : float, default None
        Average over intervals between [w[i]-dw,w[i]+dw] to average over a detector pixel width.
        If None dw is half the interval to neighbouring points.
        If 0 the value is only linear interpolated to w values and not averaged (about 10 times faster).

    Notes
    -----
    For averaging over intervals scipy.interpolate.CubicSpline is used with integration in the intervals.

    Returns
    -------
    dataArray

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100:0.5]
     start={'s0':6,'m0':0,'a0':1,'s1':None,'m1':0,'a1':1,'bgr':0.00}
     resolution=js.dynamic.resolution_w(w,**start)
     p=js.grace()
     p.plot(resolution)
     p.plot(js.dynamic.shiftAndBinning(resolution,w0=5,dw=0))

    """
    if w is None:  w=data.X.copy()
    data.X=data.X+w0
    if dw == 0:
        iwY = data.interp(w )
    else:
        if dw is None:
            dw=np.diff(w)
        else:
            dw=np.zeros(len(w)-1)*dw
        csp = scipy.interpolate.CubicSpline(data.X, data.Y)
        iwY = [csp.integrate(wi - dwl, wi + dwr)/(dwl+dwr) for wi,dwl,dwr in zip(w,np.r_[0,dw],np.r_[dw,0] )]
    result=dA(np.c_[w,iwY].T)
    result.setattr(data)
    result.setColumnIndex(data)

    return result


