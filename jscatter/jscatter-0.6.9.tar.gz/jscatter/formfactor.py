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

"""
Particle form factors for scattering.

If possible the scattering intensity (Iq) of a single particle with real scattering length densities is calculated.
It is the normalized particle form factor (Fq) if the scattering length is not unique defined as e.g. for beaucage model.

The scattering per particle is :math:`I(q)= I_0 F(q)` with particle form factor :math:`F(q)=<F_a(q)F^*_a(q)>=<|F_a(q)|^2>`
and particle scattering amplitude :math:`F_a(q)`. :math:`<>` indicates the ensemble average.

.. math:: F_a(q)= \int_V b(r) e^{iqr} \mathrm{d}r  / \int_V b(r) \mathrm{d}r  = \sum_N b_i e^{iqr}  / \sum_N b_i

The forward scattering per particle is :math:`I_0=V_p^2(SLD-solventSLD)^2` with particle volume :math:`V_p`.

In this module units for :math:`I(q)` and :math:`I_0`   are :math:`nm^2=10^{-14} cm^2` per particle.

The scattering of particles with concentration c in mol/liter in units of :math:`\\frac{1}{cm}`
is :math:`I_{[1/cm]}(q)=N_A \\frac{c}{1000} 10^{-14} I_{[nm^2]}(q)`.


Some scattering length densities as guide to choose realistic values for SLD and solventSLD:
 - neutron scattering  unit nm^-2:
    - protonated polyethylene glycol = 0.640e-6 A^-2 = 0.640e-4 nm^-2
    - SiO2                           = 4.186e-6 A^-2 = 4.186e-4 nm^-2
    - D2O                            = 6.335e-6 A^-2 = 6.335e-4 nm^-2
    - H2O                            =-0.560e-6 A^-2 =-0.560e-4 nm^-2
    - gold                           = 4.400e-6 A^-2 = 4.400e-4 nm^-2

 - Xray scattering  unit nm^-2:
    - polyethylene glycol            = 1.09e-3 nm^-2 = 387 e/nm**3
    - SiO2                           = 2.20e-3 nm^-2 = 781 e/nm**3
    - D2O                            = 0.94e-3 nm^-2 = 332 e/nm**3
    - H2O                            = 0.94e-3 nm^-2 = 333 e/nm**3
    - protein                        = 1.20e-3 nm^-2 = 433 e/nm**3
    - gold                           = 12.9e-3 nm^-2 =4589 e/nm**3

Return values are dataArrays were useful. To get only Y values use .Y

"""
from __future__ import division
import re
import inspect,sys
import os
import math,cmath
import scipy
import scipy.integrate
import scipy.constants as constants
import scipy.special as special
from scipy.spatial import distance
import numpy as np
import warnings

from .dataarray import dataArray as dA
from .dataarray import dataList as dL
from . import formel
from . import parallel
from . import structurefactor as sf


_path_=os.path.realpath(os.path.dirname(__file__))

# variable to allow printout for debugging as if debug:print 'message'
debug=False


def guinier(q,Rg=1,A=1):
    """
    Classical Guinier
    
    see genGuinier with alpha=0

    Parameters
    ----------
    q :array
    A : float
    Rg : float

    """
    return genGuinier(q,Rg=Rg,A=A,alpha=0)

def genGuinier(q,Rg=1,A=1,alpha=0):
    """
    Generalized Guinier approximation for low wavevector q scattering q*Rg< 1-1.3
    
    Parameters
    ----------
    q : array of float
        wavevector
    Rg : float
        radius of gyration in units=1/q
    alpha : float
        shape [α = 0] spheroid,    [α = 1] rod-like    [α = 2] plane
    A : float
        amplitudes
    
    Returns
    -------
    dataArray [q,Fq]

    Notes
    -----    
    | Quantitative analysis of particle size and shape starts with the Guinier approximations.
    | For three-dimensional objects the Guinier approximation is given by
    | I(q) = exp( − Rg**2*q**2 / 3)
    | This approximation can be extended also to rod-like and plane objects by
    | I(q) =(1 if α=0 or (α*pi*q^-α) if α=(1 or 2) ) * A*exp( − Rg^2q^2 / (3-α))

    If the particle has one dimension of length L, that is, much larger than
    the others (i.e., elongated, rod-like, or worm-like), then there is a q
    range such that qR_c < 1 <<  qL, where α = 1.

    for more details see
    http://sasfit.ingobressler.net/manual/Generalized_Guinier_Approximation

    """
    q=np.atleast_1d(q)
    if alpha==0:
        pre=1
    elif alpha==1 or alpha==2:
        pre=alpha*np.pi*q**-alpha
    else:
        raise TypeError('alpha needs to be in 0,1,2')
    I=pre*A*np.exp(-Rg**2*q**2/(3-alpha))
    result=dA(np.c_[q,I].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Fq'
    result.Rg=Rg
    result.A=A
    result.alpha=alpha
    result.modelname=sys._getframe().f_code.co_name
    return result

def beaucage(q,Rg=1,G=1,d=3):
    """
    Beaucage introduced a model based on the polymer fractal model. 

    Beaucage used the numerical integration form (Benoit, 1957) although the analytical integral form was available [1]_.
    The Beaucage (1995, 1996) model is characterized by three fitting parameters:

    Parameters
    ----------
    q : array
        wavevector
    Rg : float
        radius of gyration in 1/q units
    G : float
        Guinier scaling factor, transition between Guinier and Porod
    d : float
        Porod exponent for large wavevectors
    
    Returns
    -------
    dataArray [q,Fq]

    Notes
    -----
    Polymer fractals:

    | d = 5/3    fully swollen chains,
    | d = 2      ideal Gaussian chains and
    | d = 3      collapsed chains. (volume scattering)
    | d = 4      surface scattering at a sharp interface/surface
    | d = 6-dim  rough surface area with a dimensionality dim between 2-3 (rough surface)
    | d = 3      Volume scattering
    | d < r      mass fractals (eg gaussian chain)

    The Beaucage model is used to analyze small-angle scattering (SAS) data from
    fractal and particulate systems. It models the Guinier and Porod regions with a
    smooth transition between them and yields a radius of gyration and a Porod
    exponent. This model is an approximate form of an earlier polymer fractal
    model that has been generalized to cover a wider scope. The practice of allowing
    both the Guinier and the Porod scale factors to vary independently during
    nonlinear least-squares fits introduces undesired artefacts in the fitting of SAS
    data to this model.

    .. [1] Analysis of the Beaucage model
            Boualem Hammouda  J. Appl. Cryst. (2010). 43, 1474–1478
            http://dx.doi.org/10.1107/S0021889810033856

    """
    q=np.atleast_1d(q)
    Rg=float(Rg)
    C=G*d/Rg**d*(6*d**2/((2.+d)*(2.+2.*d)))**(d/2.)*special.gamma(d/2.)
    I=G*np.exp(-q**2*Rg**2/3.)+C/q**d*(special.erf(q*Rg/6**0.5))**(3*d)
    I[q==0]=1
    result=dA(np.c_[q,I].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Fq'
    result.GuinierScalingfactor=G
    result.GuinierDimension=d
    result.Rg=Rg
    result.modelname=sys._getframe().f_code.co_name
    return result

def _fa_sphere(qr):
    """
    scattering amplitude sphere with catching the zero
    """
    fa=lambda qr:3/qr**3*(np.sin(qr)-qr*np.cos(qr))
    return np.piecewise(qr,[qr==0],[1,fa])

def sphere(q,radius,contrast=1):
    """
    Scattering of a single homogeneous sphere.

    Parameters
    ----------
    q : float
        wavevector  in units of 1/nm
    radius : float
        radius in units nm
    contrast : float, default=1
        difference in scattering length to the solvent = contrast 

    Returns
    -------
    dataArray [q,Iq]
    Iq    scattering intensity
    .I0   forward scattering
    
    Notes
    -----
    The first minimum of the form factor is at q*R=4.493

    www.ncnr.nist.gov/resources/sansmodels/Sphere.html

    """
    R=radius
    qr=np.atleast_1d(q)*R
    f0=(4/3.*np.pi*R**3*contrast)**2 # forward scattering q=0
    ffQR=f0*_fa_sphere(qr)**2
    result=dA(np.c_[q,ffQR].T)
    result.columnname='q; Iq'
    result.setColumnIndex(iey=None)
    result.radius=radius
    result.I0=f0
    result.contrast=contrast
    result.modelname=sys._getframe().f_code.co_name
    return result

def sphereFuzzySurface(q,R,sigmasurf,contrast):
    """
    Scattering of a sphere with a fuzzy interface.

    Parameters
    ----------
    q : float
        wavevector  in units of 1/(R units)
    R : float
        The particle radius R represents the radius of the particle 
        where the scattering length density profile decreased to 1/2 of the core density.
    sigmasurf : float 
        sigmasurf is the width of the smeared particle surface.
    contrast : float
        difference in scattering length to the solvent = contrast 
        
    Returns
    -------
    dataArray  [q, Iq]
    Iq    scattering intensity related to sphere volume.
    .I0   forward scattering
    
    Notes
    -----
    The "fuzziness" of the interface is defined by the parameter sigmasurf. The particle
    radius R represents the radius of the particle where the scattering length density profile
    decreased to 1/2 of the core density. sigmasurf is the width of the smeared particle
    surface. The inner regions of the microgel that display a higher density are described by
    the radial box profile extending to a radius of approximately Rbox ~ R - 2(sigma). In
    dilute solution, the profile approaches zero as Rsans ~ R + 2(sigma).
    
    References
    ----------
    .. [1] M. Stieger, J. S. Pedersen, P. Lindner, W. Richtering, Langmuir 20 (2004) 7283-7292
    
    """
    Q=np.atleast_1d(q)
    f0=(4/3.*np.pi*R**3*contrast)**2 # forward scattering q=0

    def _ff(q):
        return f0*(3/(q*R)**3*(np.sin(q*R)-q*R*np.cos(q*R))*np.exp(-sigmasurf**2*q**2/2.))**2

    ffQR=np.piecewise(q,[q==0],[f0,_ff])
    result=dA(np.c_[q,ffQR].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Fq'
    result.HsRadius=R
    result.I0=f0
    result.contrast=contrast
    result.sigmasurf=sigmasurf
    result.modelname=sys._getframe().f_code.co_name
    return result

def sphereCoreShell(q,Rc,Rs,bc,bs,solventSLD=0):
    """
    Scattering of a spherical core shell particle.

    Parameters
    ----------
    q : float
        wavevector  in units of 1/(R units)
    Rc,Rs : float
        radius core and radius of shell
        Rs>Rc 
    bc,bs : float
        contrast to solvent scattering length density of core and shell
    solventSLD : float, default =0
        scattering length density of the surrounding solvent
        if equal to zero (default) then in profile the contrast is given
    
    Returns
    -------
    dataArray [wavevector ,Iq ]
    
    Notes
    -----
    Calls multiShellSphere.

    """
    return multiShellSphere(q,[Rc,Rs-Rc],[bc,bs],solventSLD=solventSLD)

def multiShellSphere(q,shellthickness,shellSLD,solventSLD=0):
    """
    Scattering of spherical multi shell particle including linear contrast variation in subshells.
    
    The results needs to be multiplied with the concentration to get the measured scattering.

    Parameters
    ----------
    q : array 
        wavevectors to calculate form factor
        unit e.g. 1/nm
    shellthickness : list of float
        thickness of shells starting from inner most 
        unit in 1/[q units]
    shellSLD : list of float or list 
        List of scattering length densities of the shells in sequence corresponding to shellthickness. unit in nm**-2
         - Innermost shell needs to be constant shell.
         - If an element of the list is itself a list of SLD values it is interpreted as equal thick subshells
           with linear progress between SLD values in sum giving shellthickness.
         - If subshell list has only one float e.g. [1e.4] the second value is the SLD of the following shell.
         - If empty list is given as [] the SLD of the previous and following shells are used as smooth transition.
    solventSLD : float, default=0
        Scattering length density of the surrounding solvent.
        If equal to zero (default) then in profile the contrast is given.
        Unit in [q unit]**2 e.g. 1/nm**2

    Returns
    -------
    dataArray [wavevector, Iq]
    Iq                  scattering cross section in units nm**2
    .contrastprofile     as radius and contrast values at edge points
    .shellthickness      consecutive shell thickness
    .shellcontrast       contrast of the shells to the solvent
    .shellradii          outer radius of the shells
    .slopes              slope of linear increase of each shell
    .outerVolume         Volume of complete sphere
    .I0                  forward scattering for Q=0
    
    Examples
    --------
    Alternating shells with 5 alternating thickness 0.4 nm and 0.6 nm with h2o, d2o scatetring contrast in vacuum::
    
     x=np.r_[0.0:10:0.01]
     ashell=js.ff.multiShellSphere(x,[0.4,0.6]*5,[-0.56e-4,6.39e-4]*5)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(ashell)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs
     
    Double shell with exponential decreasing exterior shell to solvent scattering::
     
     x=np.r_[0.0:10:0.01]
     def doubleexpshells(q,d1,d2,e3,sd1,sd2,sol):
        return js.ff.multiShellSphere(q,[d1,d2,e3*3],[sd1,sd2,((sd2-sol)*np.exp(-np.r_[0:3:9j]))],solventSLD=sol)
     dde=doubleexpshells(x,0.5,0.5,1,1e-4,2e-4,0)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(dde)
     p[1].plot(dde.contrastprofile,li=1) # a countour of the SLDs
    
    Notes
    -----
    The solution is unstable (digital resolution) for really low QR values, which are set to the I0 scattering.
    
    """
    if isinstance(shellSLD,(float,int)): shellSLD=[shellSLD]
    if isinstance(shellthickness,(float,int)): shellthickness=[shellthickness]
    if len(shellSLD)!=len(shellthickness):
        raise Exception(
            'shellSLD and shellthickness should be of same length but got:%i!=%i'%(len(shellSLD),len(shellthickness)))
    Q=np.array(q)
    shelld=[]        # list of shellthicknesses
    shelltype=[]     # list of types
    SLDs=[]          # constant scattering length density of inner radius to outer radius of shell
    Slopes=[]        # linear slope from inside to outside of a shell
    for i,sld in enumerate(shellSLD):
        if isinstance(sld,(float,int)):         # a normal constant shell only ffsph will be used
            shelld.append(shellthickness[i])
            shelltype.append(0)
            SLDs.append(sld)
            Slopes.append(0)
        elif shellthickness[i]==0:
            shelld.append(shellthickness[i])
            shelltype.append(0)
            SLDs.append(sld[0])
            Slopes.append(0)
        else:                                   # a sphere with lin progress
            if i==0:
                raise Exception('innermost shell needs to be constant contrast even if it is small!!')
            if len(sld)==0:         # linear between neighboring shells
                if i==0:
                    raise Exception('A SLD at zero (first shell) should be defined')
                shelld.append(shellthickness[i])
                shelltype.append(1)
                SLDs.append(shellSLD[i-1])
                Slopes.append((shellSLD[i+1]-shellSLD[i-1])/shellthickness[i])
            elif len(sld)==1:       # linear to following with starting value
                shelld.append(shellthickness[i])
                shelltype.append(1)
                SLDs.append(sld[0])
                Slopes.append((shellSLD[i+1]-sld[0])/shellthickness[i])
            else:
                shelld.append([shellthickness[i]/(len(sld)-1)]*(len(sld)-1))
                shelltype.append([1]*(len(sld)-1))
                SLDs.append(sld[:-1])
                slda=np.array(sld)
                Slopes.append((slda[1:]-slda[:-1])/(shellthickness[i]/(len(sld)-1)))
    SLDs=np.hstack(SLDs)
    shelld=np.hstack(shelld)
    shelltype=np.hstack(shelltype)
    Slopes=np.hstack(Slopes)
    radii=np.cumsum(shelld)

    # subtract solvent to have in any case the contrast to the solvent
    dSLDs=SLDs-solventSLD
    #  Volume  *  formfactor
    fflin=lambda qr,r:4/3.*np.pi*r*r*r*3.*r*( 2.*qr*np.sin(qr)-(qr*qr-2.)*np.cos(qr))/qr/qr/qr/qr # lin increasing part
    ffsph=lambda qr,r:4/3.*np.pi*r*r*r*3.*(np.sin(qr)-qr*np.cos(qr))/qr/qr/qr                     # constant part

    def _ff(QQ,r):
        # outer integration boundary r
        Pc=dSLDs*ffsph(QQ[:,None]*r,r)
        if len(r)>1:   # subtract lower integration boundary
            # innermost shell has r==0 and is not calculated
            Pc[:,1:]=Pc[:,1:]-dSLDs[1:]*ffsph(QQ[:,None]*r[:-1],r[:-1])
        Pl=Slopes*fflin(QQ[:,None]*r,r)
        if len(r)>1:   # subtract lower integration boundary
            Pl[:,1:]=Pl[:,1:]-Slopes[1:]*fflin(QQ[:,None]*r[:-1],r[:-1])
        return (Pc+Pl).sum(axis=1)**2

    # forward scattering Q=0 -------------
    dslds=4/3.*np.pi*radii**3*dSLDs
    dslds[:-1]=dslds[:-1]-4/3.*np.pi*radii[:-1]**3*dSLDs[1:]
    slr=np.pi*radii**4*Slopes
    slr[:-1]=slr[:-1]-np.pi*radii[:-1]**4*Slopes[1:]
    f0=(dslds+slr).sum()**2
    # ------------------------------------
    # the calculation shows up to be unstable for really small Qr as the binary resolution shows up in the lin part.
    # therefore we limit it to the f0 value below a threshold; the error is of order 1e-4
    PP=np.piecewise(Q,[Q<5e-3/max(radii)],[f0,_ff],radii)
    result=dA(np.c_[q,PP].T)
    result.columnname='q; Iq'
    result.shellthickness=shelld
    result.shellcontrast=SLDs
    result.shellradii=radii
    contrastprofile=np.c_[np.r_[radii-shelld,radii],np.r_[SLDs,SLDs+Slopes*shelld]].T
    result.contrastprofile=contrastprofile[:,np.repeat(np.arange(len(SLDs)),2)+np.tile(np.r_[0,len(SLDs)],len(SLDs))]
    result.slopes=Slopes
    result.outerVolume=4./3*np.pi*max(radii)**3
    result.I0=f0
    result.shelltype=shelltype
    result.modelname=sys._getframe().f_code.co_name
    return result

def cylinder(q,L,radius,SLD,solventSLD=0,alpha=[0,np.pi/2]):
    """
    cylinder form factor (open cap)

    see multiShellCylinder

    """
    return multiShellCylinder(q,L,[radius],[SLD],solventSLD=solventSLD,alpha=alpha)

def _fqcylinder(q, r, L, angle):
    """
    cylinder form factor amplitude, save for q=0 and q<0 result is zero

    q : wavevectors
    r : shell thickness , a list or array !!
    L : length of cylinder, L=0 is infinitly long cylinder
    angle : angle between axis and scattering vector q in rad

    q<0 result is zero needed in ellipsoidFilledCylinder

    """
    # deal with possible zero in q
    if isinstance(q, (float, int)):
        q = np.r_[q]
    result = np.zeros((len(q), len(r)))
    if angle != 0:
        sina = np.sin(angle)
        cosa = np.cos(angle)
    else:
        sina = 1
        cosa = 1
    if L > 0 and r[0]>0:
        fq0 = 2. * np.pi * r ** 2 * L
        fqq = lambda q: fq0 * special.j1(q[:,None]*r*sina)/(q[:,None]*r*sina)*special.j0(q[:,None]*L/2.*cosa)
    elif r[0]>0:
        fq0 = 2. * np.pi * r ** 2 * 1
        fqq = lambda q: fq0 * special.j1(q[:, None] * r * sina) / (q[:, None] * r * sina)
    elif L>0:
        fq0 = 2. *  L
        fqq = lambda q: fq0 * special.j0(q[:,None]*L/2.*cosa)

    result[np.where(q > 0)[0], :] = fqq(q[np.where(q > 0)])
    result[np.where(q == 0)[0], :] = fq0 * 0.5
    return result

def _fqcylindercap(q, r, L, angle,h,n=21):
    # Equ 1 in Kaya & Souza  J. Appl. Cryst. (2004). 37, 508±509  DOI: 10.1107/S0021889804005709
    # integrate by fixed GAussian at positions t and weights w
    j1=special.j1
    x, w = formel._cached_p_roots(n)
    x = np.real(x)
    if isinstance(q, (float, int)):
        q = np.r_[q]
    if angle != 0:
        sina = np.sin(angle)
        cosa = np.cos(angle)
    else:
        sina = 1
        cosa = 1
    R=(h**2+r**2)**0.5
    lowlimit=-h/R
    uplimit=1
    t = ((uplimit - lowlimit) * (x[:,None,None] + 1) / 2.0 + lowlimit)   # first axis for x
    result = np.zeros((len(t),len(q), len(r)))
    cap=lambda q:4*np.pi*r**3*np.cos(q[:,None]*cosa*(r*t + h + L/2)) * \
                 (1-t**2)*(j1(q[:,None]*r*sina*(1-t**2)**0.5))/(q[:,None]*r*sina*(1-t**2)**0.5)
    cap0=4*np.pi*r**3*(1-t**2)

    result[:,np.where(q > 0)[0], :] = (uplimit - lowlimit) / 2.0 *cap(q[np.where(q > 0)])
    result[:,np.where(q == 0)[0], :] = (uplimit - lowlimit) / 2.0 *cap0 * 0.5

    # multiply by weight and sum over weights
    return (result*w[:,None,None]).sum(axis=0)

def multiShellCylinder(q,L,shellthickness,shellSLD,solventSLD=0,alpha=[0,np.pi/2],h=None,nalpha=30,ncap=31):
    """
    Multi shell cylinder with caps in solvent averaged over axis orientations.

    Each shell has a constant SLD and may have a cap with same SLD sequence.
    Caps may be globular (barbell) or small (like lenses).
    For zero length L a lens shaped disc or  a double sphere like shape is recovered.

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    L : float
        Length of cylinder, units nm
        L=0 infinite cylinder if h=None.
    shellthickness : list of float or float, all >0
        Thickness of shells in sequence, units nm.
        radii r=cumulativeSum(shellthickness)
    shellSLD : list of float or float
        Scattering length density of shells in nm^-2.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    h : float, default=None
        Geometry of the caps with cap radii R=(r**2+h**2)**0.5
        h is distance of cap center with radius R from the flat cylinder cap and r as radii of the cylinder shells.
         - None No caps, flat ends as default.
         - 0 cap radii equal cylinder radii (same shellthickness as cylinder shells)
         - >0 cap radius larger cylinder radii as barbell
         - <0 cap radius smaller cylinder radii as lens caps
    alpha : float, [float,float] , unit rad
        Orientation, angle between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 30
        Number of points in Gauss integration along alpha.
    ncap : int, default=31
        Number of points in Gauss integration for cap.

    Returns
    -------
    dataArray [q ,Iq ]
    .outerCylinderVolume
    .Radius
    .cylindeLength
    .alpha
    .shellthickness
    .shellSLD
    .solventSLD
    .modelname
    .contrastprofile
    .capRadii

    Notes
    -----
    Multishell of types:
     - flat cap cylinder      L>0, radii>0, h=None
     - lens cap cylinder      L>0, radii>0, h<0
     - globular cap cylinder  L>0, radii>0, h>0
     - lens                   L=0, radii>0, h<0
     - barbell no cylinder    L=0, radii>0, h>0
     - infinite flat disc     L=0. h=None

    .. image:: barbell.png
     :align: center
     :height: 150px
     :alt: Image of barbell

    Examples
    --------
    Alternating shells with different thickness 0.3 nm h2o and 0.2 nm d2o in vacuum::

     x=np.r_[0.0:10:0.01]
     ashell=js.ff.multiShellCylinder(x,20,[0.4,0.6]*5,[-0.56e-4,6.39e-4]*5)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(ashell)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs

    Double shell with exponential decreasing exterior shell to solvent scattering::

     x=np.r_[0.0:10:0.01]
     def doubleexpshells(q,L,d1,d2,e3,sd1,sd2,sol):
        return js.ff.multiShellCylinder(q,L,[d1,d2,e3*3],[sd1,sd2,((sd2-sol)*np.exp(-np.r_[0:3:9j])+sol)],solventSLD=sol)
     dde=doubleexpshells(x,10,0.5,0.5,1,1e-4,2e-4,0)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(dde)
     p[1].plot(dde.contrastprofile,li=1) # a countour of the SLDs

    Cylinder with cap::

     x=np.r_[0.1:10:0.01]
     p=js.grace()
     p.title('Comaprison of dumbell cylinder with simple models')
     p.subtitle('thin lines correspnd to simple models as sphere and dshell sphere')
     p.plot(js.ff.multiShellCylinder(x,0,[10],[1],h=0),sy=[1,0.5,2],le='simple sphere')
     p.plot(js.ff.sphere(x,10),sy=0,li=1)
     p.plot(js.ff.multiShellCylinder(x,0,[2,1],[1,2],h=0),sy=[1,0.5,3],le='double shell sphere')
     p.plot(js.ff.multiShellSphere(x,[2,1],[1,2]),sy=0,li=1)
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=-5),sy=[1,0.5,4],le='thin lens cap cylinder=flat cap cylinder')
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=None),sy=0,li=[1,2,1],le='flat cap cylinder')
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=-0.5),sy=0,li=[3,2,6],le='thick lens cap cylinder')
     p.yaxis(scale='l')
     p.xaxis(scale='l')
     p.legend(x=0.15,y=0.01)

    References
    ----------
    Single cylinder

    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955)
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Cylinder.html

    Double cylinder

    .. [3] Use of viscous shear alignment to study anisotropic micellar structure by small-angle neutron scattering,
           J. B. Hayter and J. Penfold J. Phys. Chem., 88:4589--4593, 1984
    .. [4] http://www.ncnr.nist.gov/resources/sansmodels/CoreShellCylinder.html

    Barbell, cylinder with small end-caps, circular lens

    .. [5] Scattering from cylinders with globular end-caps
           Kaya (2004). J. Appl. Cryst. 37, 223-230]     DOI: 10.1107/S0021889804000020
           Scattering from capped cylinders. Addendum
           H. Kaya and Nicolas-RaphaeÈl de Souza
           J. Appl. Cryst. (2004). 37, 508-509  DOI: 10.1107/S0021889804005709

    """
    if isinstance(shellSLD,(float,int)): shellSLD=[shellSLD]
    if isinstance(shellthickness,(float,int)): shellthickness=[shellthickness]
    shellthickness
    if len(shellSLD)!=len(shellthickness):
        raise Exception(
            'shellSLD and shellthickness should be of same length but got:%i!=%i'%(len(shellSLD),len(shellthickness)))
    Q=np.atleast_1d(q)
    shelld=[]        # list of shellthicknesses
    SLDs=[]          # constant scattering length density of inner radius to outer radius of shell
    for i,sld in enumerate(shellSLD):
        if isinstance(sld,(float,int)):         # a normal constant shell only ffsph will be used
            shelld.append(abs(shellthickness[i]))
            SLDs.append(sld)
        else:                                   # a shell with lin progress
            shelld.append([abs(shellthickness[i])/(len(sld)-1)]*(len(sld)-1))
            SLDs.append(sld[:-1])
    SLDs=np.hstack(SLDs)
    shelld=np.hstack(shelld)
    radii=np.cumsum(shelld)
    # subtract solvent to have in any case the contrast to the solvent
    dSLDs=SLDs-solventSLD

    # cylinder scattering amplitude
    _fq=_fqcylinder
    _fc=_fqcylindercap

    def _ff(QQ,r,L,angle):
        # formfactor of a cylinder with orientation angle alpha
        # outer integration boundary r
        QQ0=np.r_[0,QQ]
        Pc=dSLDs*_fq(QQ0,r,L,angle)
        if h is not None and np.all(r>0):
            # calc cap contribution
            Pcap=dSLDs*_fc(QQ0,r,L,angle,h,ncap)
        if len(r)>1:   # subtract lower integration boundary
            #  r==0 is not calculated
            Pc[:,1:]=Pc[:,1:]-dSLDs[1:]*_fq(QQ0,r[:-1],L,angle)
            if h is not None and np.all(r>0):
                # calc cap contribution
                Pcap[:, 1:] = Pcap[:, 1:] - dSLDs[1:] * _fc(QQ0, r[:-1], L, angle,h,ncap)
        if h is not None and np.all(r>0):
            # this avoids the infinite thin disc to be added
            if L>0:
                Pc2 = (Pc+Pcap).sum(axis=1) ** 2
            else:
                Pc2 = (Pcap).sum(axis=1) ** 2
        else:
            # cylinder without cap
            Pc2=(Pc).sum(axis=1)**2
        result=dA(np.c_[QQ,Pc2[1:]*np.sin(angle)].T)
        #store the forward scattering
        result.I0=Pc2[0]
        return result

    # test if alpha is angle or range
    try:
        if alpha[0]==alpha[1]:
            alpha=alpha[0]
    except:
        pass
    if isinstance(alpha,(float,int)):
        # single angle
        result=_ff(Q,radii,L,alpha)

    else:
        # integrate over range
        alpha[1]=min(alpha[1],np.pi/2.)
        alpha[0]=max(alpha[0],0.)
        result = formel.parQuadratureFixedGauss(_ff, alpha[0], alpha[1], 'angle',n=nalpha, QQ=Q, r=radii, L=L)

    result.outerCylinderVolume=np.pi*radii[-1]**2*L
    result.setColumnIndex(iey=None)
    result.columnname='q; Iq'
    result.Radius=radii[-1]
    result.cylindeLength=L
    result.alpha=alpha
    result.shellthickness=np.abs(shellthickness)
    result.shellSLD=shellSLD
    result.solventSLD=solventSLD
    if h is not None:
        result.capRadii=radii*(1+h**2)**0.5
        if h!=0:
            result.capRadii *= np.sign(h)
    contrastprofile=np.c_[np.r_[radii-shelld,radii],np.r_[SLDs,SLDs]].T
    result.contrastprofile=contrastprofile[:,np.repeat(np.arange(len(SLDs)),2)+np.tile(np.r_[0,len(SLDs)],len(SLDs))]
    result.modelname=sys._getframe().f_code.co_name
    return result

def gaussianChain(q,Rg):
    """
    Formfactor of a gaussian polymer chain (Debye model)

    Parameters
    ----------
    q : array
        scattering vector unit eg  1/A or 1/nm
    Rg : float
        radius of gyration  units in 1/unit(q)

    Returns
    -------
    dataArray [q,Fq]
    .radiusOfGyration

    Notes
    -----
    for large q    ~q**-2

    """

    q=np.atleast_1d(q)
    qr2=Rg**2*q**2
    res=np.piecewise(qr2,[qr2==0],[1,lambda x:2*(np.exp(-x)-1+x)/x**2])
    result=dA(np.c_[q,res].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Fq'
    result.radiusOfGyration=Rg
    result.modelname=sys._getframe().f_code.co_name
    return result

def wormlikeChain(q,N,a,R=None,SLD=1,solventSLD=0,rtol=0.02):
    r"""
    Scattering of a wormlike chain, which correctly reproduces the rigid-rod and random-coil limits.

    The forward scattering is :math:´I0=V^2(SLD-solventSLD)^2´ volume :math:´V=\piR^2N´.

    Parameters
    ----------
    q : array
        wavevectors in 1/nm
    N : float
        Chain length, units of 1/q
    a : float
        Persistence length with l=2a l=Kuhn length (segment length), units of nm.
    R : float
        Radius in units of nm.
    SLD : float
        Scattering length density segments.
    solventSLD :
        Solvent scattering length density.
    rtol : float
        Maximum relative tolerance in integration.

    Returns
    -------
    dataArray [q, Iq]
    .chainRadius
    .chainLength
    .persistenceLength
    .Rg
    .volume
    .contrast

    Examples
    --------
    ::

     import jscatter as js
     p=js.grace()
     p.multi(2,1)
     p.title('figure 3 (2 scaled) of ref Kholodenko Macromolecules 26, 4179 (1993)',size=1)
     q=js.loglist(0.01,10,100)
     for a in [1,2.5,5,20,50,1000]:
         ff=js.ff.wormlikeChain(q,200,a)
         p[0].plot(ff.X,200*ff.Y*ff.X**2,legend='a=%.4g' %ff.persistenceLength)
         p[1].plot(ff.X,ff.Y,legend='a=%.4g' %ff.persistenceLength)
     p[0].legend()
     p[0].yaxis(label='Nk\S2\NS(k)')
     p[1].xaxis(label='k',scale='l')
     p[1].yaxis(label='S(k)',scale='l')
     #
     p=js.grace()
     p.multi(2,1)
     p.title('figure 4 of ref Kholodenko Macromolecules 26, 4179 (1993)',size=1)
     # fig 4 seems to be wrong scale in [1]_ as for large N with a=1 fig 2 and 4 should have same plateau.
     a=1
     q=js.loglist(0.01,4./a,100)
     for NN in [1,20,50,150,500]:
         ff=js.ff.wormlikeChain(q,NN,a)
         p[0].plot(ff.X*a,NN*a*ff.Y*ff.X**2,legend='N=%.4g' %ff.chainLength)
         p[1].plot(ff.X,ff.Y,legend='a=%.4g' %ff.persistenceLength)
     p[0].legend()
     p[0].yaxis(label='(N/a)(ka)\S2\NS(k)')
     p[0].xaxis(label='ka')
     p[1].xaxis(label='k',scale='l')
     p[1].yaxis(label='S(k)',scale='l')

    Notes
    -----
    From [1]_ :
        The Kratky plot (Figure 4 ) is not the most convenient
        way to determine a as was pointed out in ref 20. Figure
        5 provides an alternative way of measuring a by plotting
        the experimentally measurable combination Nk2S(k)
        versus a for fixed wavelength k. As Figure 5 indicates,
        this plot is rather insensitive to the chain length N and
        therefore is universal. The numerical analysis of eq 17
        shows that this remains true for as long as k is not too
        small. Taking into account that the excluded-volume
        effects leave S(k) practically unchanged (e.g., see Figures
        2 and 4 of ref 231, the plot of Figure 5 can serve as a useful
        alternative to the Kratky plot which, in addition, does not
        suffer from the polydispersity effects

    - Rg is calculated according to equ 20 in [2]_ and [3]_.

    References
    ----------
    .. [1] Analytical calculation of the scattering function for polymers of arbitrary flexibility using the dirac propagator,
           A. L. Kholodenko, Macromolecules, 26:4179--4183, 1993
    .. [2] The structure factor of a wormlike chain and the random-phase-approximation solution for the spinodal line of a diblock copolymer melt
           Zhang X et. al. Soft Matter 10, 5405 (2014)
    .. [3] Models of Polymer Chains
           Teraoka I. in Polymer Solutions: An Introduction to Physical Properties pp: 1-67, New York, John Wiley & Sons, Inc.


    """
    a2=2.*float(a)
    q=np.atleast_1d(q)        # row vector
    limit=100  # limit to avoid exp overflow
    x=3*N/a2
    z=np.c_[0:x:1000*1j]   # column vector

    EF=np.sqrt(np.sign(a2*q/3.-1)*((a2*q/3.)**2-1))
    EFiszero=(EF==0)
    EF[EFiszero]=1 #to avoid EF=0
    # fz is [ z , q ] matrix
    def FZ(qq,zz):
        mfz=np.zeros((zz.shape[0],qq.shape[0]))
        # now fill it
        mfz[(0<zz)&(zz<limit)&(a2*qq<=3)] = (np.sinh(zz[(0<zz)&(zz<limit),None]*EF[None,a2*qq<=3])/np.sinh(zz[(0<zz)&(zz<limit),None])/EF[None,a2*qq<=3]).flatten()
        # for to large zz we avoid expz>limit and use sinh(EF*zz)/sinh(zz)=exp(zz*(Ef-1)) for zz>limit
        mfz[(zz>=limit)&(a2*qq<=3)] = (np.exp(zz[zz>=limit            ,None]*(EF[None,a2*qq<=3]-1))/EF[None,a2*qq<=3]).flatten()
        mfz[(0<zz)&(zz<limit)&(a2*qq>3)] = (np.sin(zz[(0<zz)&(zz<limit) ,None]*EF[None,a2*qq>3])/np.sinh(zz[(0<zz)&(zz<limit),None])/EF[None,a2*qq>3]).flatten()
        #mfz[(zz>limit          ) & (a2*qq >3)] = 0    # default is zero
        # for zz=0  limes is  1 in both cases
        mfz[zz[:,0]==0,:]=1
        if np.any(EFiszero):
            # catch fz  when EF is zero and assigne correct value
            mfz[(0<zz)&(zz<limit)&EFiszero]=(zz[(0<zz)&(zz<limit)]/np.sinh(zz[(0<zz)&(zz<limit)]))
            #mfz[         (zz>limit)  & EFiszero]=0   # default is zero
        return mfz
    # integrate I1 and I2 from above matrix
    fz=FZ(q,z)
    I1=scipy.integrate.simps(fz,z,axis=0)
    I2=scipy.integrate.simps(fz*z,z,axis=0)
    P0=2./x*(I1-I2/x)

    while True:
        # adaptive integration to increase accuracy stepwise
        nz=np.c_[0:x:(2*len(z)-1)*1j]
        nfz=np.zeros((nz.shape[0],q.shape[0]))
        nfz[::2,:]=fz
        nfz[1::2,:]=FZ(q,nz[1::2]) # each second is new element
        I1=scipy.integrate.simps(nfz,nz,axis=0)
        I2=scipy.integrate.simps(nfz*nz,nz,axis=0)
        nP0=2./x*(I1-I2/x)
        if max(abs(nP0-P0)/abs(nP0))<rtol:
            P0=nP0
            break
        else:
            z=nz
            fz=nfz
            P0=nP0
    # now do the volume and sld
    if R is not None:
        Pcs=(2*special.j1(q * R )/q/R)**2
        V=np.pi*R*R*N
        sld=SLD-solventSLD
    else:
        Pcs=1
        R=0
        V=1
        sld=1
    result=dA(np.c_[q,V**2*sld**2*P0*Pcs].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Iq'
    result.chainRadius=R
    result.chainLength=N
    result.persistenceLength=a
    b=a/2.
    result.Rg=np.sqrt((b*N/6.)*(1-1.5*b/N+1.5*(b/N)**2-0.75*(b/N)**3*(1-np.exp(-2*N/b))))
    result.volume =V
    result.contrast=sld
    result.columnname='q; Iq'
    result.modelname=sys._getframe().f_code.co_name
    return result

def sphereGaussianCorona(q,R,Rg,Ncoil,coilequR,coilSLD=0.64e-4,sphereSLD=4.186e-4 ,solventSLD=6.335e-4,d=1):
    """
    Scattering of a sphere surrounded by gaussian coils as model for grafted polymers on particle e.g. a micelle.

    The additional scattering is uniformly distributed at the surface, which might fail for lower aggregation
    numbers as 1, 2, 3.
    Instead of aggregation number in [1]_ we use sphere volume and a equivalent volume of the gaussian coils.

    Parameters
    ----------
    q: array of float
        wavevectors in units 1/nm
    R : float
        sphere radius unit nm
    Rg : float
        radius of gyration of coils unit nm
    d : float, default 1
        Coils centre loacated d*Rg away from the sphere surface
    Ncoil : float
        number of coils at the surface (aggregation number)
    coilequR : float
        Equivalent radius to calc volume of the coil mass if densely packed as a sphere.
        Needed to calculate absolute scattering of the coil.
    coilSLD : float
        Scattering length density of coil.  unit nm^-2.
        default hPEG = 0.64*1e-6 A^-2 = 0.64*1e-4 nm^-2
    sphereSLD : float
        Scattering length density of sphere.unit nm^-2.
        default SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of solvent. unit nm^-2.
        default D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2

    Returns
    -------
    dataArray [q,Iq]
    .coilRg
    .sphereRadius
    .numberOfCoils
    .coildistancefactor
    .coilequVolume
    .coilSLD
    .sphereSLD
    .solventSLD

    Notes
    -----
    The defaults result in a silica sphere with hPEG grafted at the surface in D2O.
     - Rg=N**0.5*b    with N monomers of length b
     - Vcoilsphere=4/3.*np.pi*coilequR**3
     - Vcoilsphere=N*monomerVolume
     - coilequR=(N*monomerVolume/(4/3.*np.pi))**(1/3.)

    References
    ----------
    .. [1] Form factors of block copolymer micelles with spherical, ellipsoidal and cylindrical cores
           Pedersen J
           Journal of Applied Crystallography 2000 vol: 33 (3) pp: 637-640
    .. [2] Hammouda, B. (1992).J. Polymer Science B: Polymer Physics30 , 1387–1390

    """
    q=np.atleast_1d(q)
    Q=np.where(q==0,q*0+1e-10,q)
    # scattering amplitude gaussian coil
    cg=coilSLD-solventSLD
    coilVolume=(4/3.*np.pi*coilequR**3)
    fa_coil=coilVolume*cg*(1-np.exp(-Rg*Q))/(Rg*Q)  #fa_coil**2 is Debye function [2]..
    # amplitude sphere
    cs=sphereSLD-solventSLD
    QR=Q*R
    f0=(4/3.*np.pi*R**3*cs) # forward scattering Q=0
    fa_sphere=f0*(3/QR**3*(np.sin(QR)-QR*np.cos(QR)))
    # total scattering from one sphere and N coils
    #  (   fa_sphere + [ fa_coil + fa_coil+.....] )**2
    res=  fa_sphere**2                                                  # sphere scattering
    res+= Ncoil*fa_coil**2                                              # N * coil scattering
    res+= 2*Ncoil*fa_sphere*fa_coil*np.sin(Q*(R+d*Rg))/(Q*(R+d*Rg))     # N times interference between one coil and one sphere
    res+= Ncoil*(Ncoil-1)*(fa_coil*np.sin(Q*(R+d*Rg))/(Q*(R+d*Rg)))**2  # interference between one coils with distance R+d*Rg

    result=dA(np.c_[q,res].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Iq'
    result.coilRg=Rg
    result.sphereRadius=R
    result.numberOfCoils=Ncoil
    result.coildistancefactor=d
    result.coilequVolume=coilVolume
    result.coilSLD =coilSLD
    result.sphereSLD=sphereSLD
    result.solventSLD=solventSLD
    result.modelname=sys._getframe().f_code.co_name
    return result

def cuboid(q, a, b=None, c=None, SLD=1, solventSLD=0, NN=300):
    """
    Formfactor of cuboid.

    Parameters
    ----------
    q : array
        Wavevector in 1/nm
    a,b,c : float, None
        Edge length, for a=b=c its a cube, Units in nm.
        If b=None b=a.
        If c=None c=b.
    SLD : float, default =1
        Scattering length density of cuboid.unit nm^-2
        e.g. SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2 for neutrons
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
        e.g. D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2 for neutrons
    NN : int
        Number of gridpoints on Fibonacci lattice is 2*NN+1 for spherical average.

    Returns
    -------
    dataArray [q,Iq]
    .edges
    .contrast
    .gridpoints

    Notes
    -----
    The orientational average is calculated on Fibonacci lattice.

    References
    ----------
    .. [1] Analysis of small-angle scattering data from colloids and polymer solutions: modeling and least-squares fitting
           Pedersen, Jan Skov Advances in Colloid and Interface Science 70, 171 (1997)
           http://dx.doi.org/10.1016/S0001-8686(97)00312-6

    """
    if b is None:
        b=a
    if c is None:
        c=b
    sld=SLD-solventSLD
    V=a*b*c
    q=np.atleast_2d(q).T
    sin=np.sin
    cos=np.cos
    sinc=np.sinc
    f=lambda q,la:sinc(q*a/2.*sin(la[0])*cos(la[1])/np.pi)* \
                  sinc(q*b/2.*sin(la[0])*sin(la[1])/np.pi)* \
                  sinc(q*c/2.*cos(la[0])           /np.pi)
    # lattice of equal distributed points, remove r component
    lattice= formel.fibonacciLatticePointsOnSphere(NN)[:, np.r_[1, 2]].T
    result=dA(np.c_[q,V**2*sld**2*(f(q,lattice)**2).mean(axis=-1)].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Iq'
    result.modelname=sys._getframe().f_code.co_name
    result.edges=[a,b,c]
    result.contrast=sld
    result.gridpoints=NN
    return result

def _scattering(point,r,q,blength,formfactor=None,rms=0,ffpolydispersity=0):
    """
    Coherent scattering of objects at positions r in direction point on sphere with length (radius) q

    Parameters
    ----------
    point : point on unit sphere 3 x 1
    q : float
        q vector length
    r : array  N x 3
        vector of objekt positions
    blength : array N
        scattering length of objects
    formfactor 2xN array
        formfactor of all objects
    rms: float
        position rms
    ffpolydispersity : float
        size rms by scaling of size

    Returns
    -------
    F(Q)*F(Q).conj() , F(Q).sum()

    pure numpy way
    """
    if ffpolydispersity>0:
        # normal distribution of size factor
        sizerms=np.random.randn(r.shape[0])*ffpolydispersity+1
        # correponding relative volume change
        volrmsfactor=sizerms**3
        volrmsfactor[sizerms<=0]=0
        fa = blength *volrmsfactor* np.interp(q*sizerms, formfactor[0, :], formfactor[1, :])
    else:
        fa=blength*np.interp(q, formfactor[0, :], formfactor[1, :])
    qx=q*point
    if rms>0:
        r=r+np.random.randn(r.shape[0],3)*rms
    iqr=np.einsum('i,ji',qx,r)*1j                             # 454 µs        iqr.shape 26135
    beiqrsum=np.einsum('i,i',fa,np.exp(iqr))
    Sq=beiqrsum*beiqrsum.conj()                               #  2 µs
    return q,Sq.real,beiqrsum.real

def _scattering_Debye(r,f,q):
    """
    Debye equation  definition as in _scattering
    """
    if q==0:
        return f.sum()**2
    # ()**2.sum()**0,5 to get absolute value |ri-rj|
    qrij=q*((r[:,np.newaxis]-r)**2).sum(axis=2)**0.5             #137 ms r.shape (1856, 3)
    np.fill_diagonal(qrij,1)                                     # 19 µs
    sinoq=np.sin(qrij)/qrij                                     #47.7 ms   still faster than np.sinc
    np.fill_diagonal(sinoq,1)                                    #19.4 µs
    Sq=np.einsum('i,j,ij->',f,f,sinoq)               # 10.3 ms
    return Sq

def cloudScattering(q, cloud, nFib=50, V=0, formfactor=None, rms=0, ffpolydispersity=0,ncpu=0):
    r"""
    Scattering of a cloud of scatterers with variable scattering length. Using multiprocessing.

    Cloud can represent any object described by a cloud of scatterers with scattering amplitudes
    as constant, sphere scattering amplitude, Gaussian scattering amplitude or explicitly given one.
    The result is normalized by sum(scattering length )**2 to equal one for q=0 (except for polydispersity).
    Rememeber that the atomic bond length are on the order 0.1-0.2 nm.

    Parameters
    ----------
    q : array, ndim= Nx1
         wavevectors in 1/nm
    cloud : array Nx3 or Nx4
        - Center of mass positions (in nm) of the N scatterers in the cloud.
        - If given cloud[3] is the scattering length :math:`b` at positions cloud[:3], otherwise :math:`b=1`.
    nFib : int
        - For nFib>0 explicit calculation of spherical average with Fibonacci lattice of 2*nFib+1 points.
        - For nFib=0 the Debye equation is used (no asymmetry factor beta, no multiprocessing, no rms, no ffpolydispersity).
    rms : float, default=0
        Root mean square displacement =<u**2>**0.5 of the positions in cloud as random (Gaussian) displacements in units nm.
        Dispacement u is random for each orientation in sphere scattering.
        rms can be used to simulate a Debye-Waller factor.
    V : float, default=0
        Volume of the scatterers for scattering amplitude (see formfactor).
    formfactor : None,'gauss','sphere','cube'
        Gridpoint scattering amplitudes F(q) are described by:
         - None    : const scattering amplitude.
         - 'sphere': Sphere scattering amplitude according to [3]_. The sphere radius is :math:`R=(\frac{3V}{4\pi})^{1/3}`
         - 'gauss' : Gaussian function :math:`b_i(q)=bVexp(- \frac{V^{2/3.}}{4\pi}q^2)` according to [2]_.
         - 'cube'  : Cube method not yet implemented.
         - Explicit isotropic form factor ff as array with [q,ff] e.g. from multishell.
           The normalized scattering amplitude fa for each gridpoint is calculated as fa=ff**0.5/fa(0).
           Missing values are linear intepolated (np.interp), q values outside interval are mapped to qmin or qmax.
    ffpolydispersity : float
        Polydispersity of the gridpoints in relative units for sphere, gauss, explicit.
        Assuming F(q*R) for each gridpoint F is scaled as F(q*f*R)  with f as normal distribution
        around 1 and standard deviation ffpolydispersity. The scattering length :math:`b` is scaled according
        to the respective volume change by f**3. (f<0 is set to zero . )
        This results in a change of the forward scattering because of the stronger weight of larger objects.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
         - not given or 0 : all cpus are used
         - int>0          : min(ncpu, mp.cpu_count)
         - int<0          : ncpu not to use
         - 1              : single core usage for testing or comparing speed to Debye

    Returns
    -------
        dataArray [q, Pq, beta]

         - .sumblength : Sum of blength with I(q=0)=sumblength**2
         - .formfactoramplitude_q : formfactoramplitude of cloudpoints according to type for all q values.

    Notes
    -----
    We calculate the scattering amplitude :math:`F(q)` for :math:`N` atoms in a volume :math:`V` with scattering length density :math:`b(r)`

    .. math:: F(q)= \int_V b(r) e^{iqr} \mathrm{d}r  / \int_V b(r) \mathrm{d}r  = \sum_N b_i e^{iqr}  / \sum_N b_i

    with the  form factor :math:`P(Q)` after orientational average :math:`<>`

    .. math:: P(Q)=< F(q) \cdot F^*(q) >=< |F(q)|^2 >

    The scattering intensity of a single object represented by the cloud is :math:`I(Q)=P(Q) \cdot V^2 \cdot (\int_V b(r) \mathrm{d}r)^2`.

    beta is the asymmetry factor [1]_ :math:`beta =|< F(q) >|^2 / < |F(q)|^2 >`

    One has to expect a peak at :math:`q=2\pi/d_{NN}` with :math:`d_{NN}` as the distance between scatterers.

    On the other side the cloud scattering can represent the scattering of a *cluster of particles* with polydispersity
    and position distortion according to root mean square displacements (rms).
    Polydispersity and rms displacements are randomly changed within the orientational average to represent
    an ensemble average (opposite to the time average of a single cluster).


    Examples
    --------
    Here we compare explicit calculation with the Debye equation as the later gets quite slow for larger numbers.
    The example is compared to the analytic solution for a sphere.
    For other shapes the grid may be better rotated away from the object symmetry or a random grid should be used.
    The example shows a good approximation with NN=20. Because of the grid peak at :math:`q=2\pi/d_{NN}`
    the grid scatterer distance :math:`d_{NN}` should be :math:`d_{NN} < \frac{1}{3} 2\pi/q_{max}` .

    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     # cubic grid points
     R=3;NN=20;nFib=50
     grid= np.mgrid[-R:R:1j*NN, -R:R:1j*NN,-R:R:1j*NN].reshape(3,-1).T
     # points inside of sphere with radius R
     p=1;p2=1*2 # p defines a superball with 1->sphere p=inf cuboid ....
     inside=lambda xyz,R:(np.abs(xyz[:,0])/R)**p2+(np.abs(xyz[:,1])/R)**p2+(np.abs(xyz[:,2])/R)**p2<=1
     insidegrid=grid[inside(grid,R)]
     q=np.r_[0:5:0.1]
     p=js.grace()
     p.title('compare formfactors of a sphere')
     ffe=js.ff.cloudScattering(q,insidegrid,nFib=nFib)    # takes about 1.9 s on single core
     p.plot(ffe,legend='cloud ff explicit')
     ffd=js.ff.cloudScattering(q,insidegrid,nFib=0)     # takes about 47 s on single core
     p.plot(ffd,legend='cloud ff Debye')
     ffa=js.ff.sphere(q,R)
     p.plot(ffa.X,ffa.Y/ffa.I0,li=1,sy=0,legend='analytic formula')
     p.legend()
     #
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     # show only each 20th point
     pxyz=insidegrid[np.random.randint(len(insidegrid),size=int(nFib**3/20))]
     #
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-5,5])
     ax.set_ylim([-5,5])
     ax.set_zlim([-5,5])
     ax.set_aspect("equal")
     plt.tight_layout()
     plt.show(block=False)

    An objekt with **explicit given formfactor** for each gridpoint.
    ::

     # 5 coreshell particles in line with polydispersity
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 4
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)
     ffe = js.ff.cloudScattering(q, rod0, formfactor=cs,nFib=100,ffpolydispersity=0.1)
     p=js.grace()
     p.plot(ffe)

    Using cloudscattering **as fit model**.

    We have to define a model that parametrizes the building of the cloud that we get fit parameters.
    As example we use two overlapping spheres. The model can be used to fit some data.
    The build of the model is important as it describes how the overlapp is treated.
    Here e.g. as average.

    ::

     #: test if distance from point on X axis
     isInside=lambda x,A,R:((x-np.r_[A,0,0])**2).sum(axis=1)**0.5<R
     #: model
     def dumbbell(q,A,R1,R2,b1,b2,bgr=0,dx=0.3,nFib=100):
         # D sphere distance
         # R1, R2 radii
         # b1,b2  scattering length
         # bgr background
         # dx grid distance not a fit parameter!!
         mR=max(R1,R2)
         # xyz coordinates
         grid=np.mgrid[-A/2-mR:A/2+mR:dx,-mR:mR:dx,-mR:mR:dx].reshape(3,-1).T
         insidegrid=grid[isInside(grid,-A/2.,R1) | isInside(grid,A/2.,R2)]
         # add blength column
         insidegrid=np.c_[insidegrid,insidegrid[:,0]*0]
         # set the corresponding blength; the order is important as here b2 overwrites b1
         insidegrid[isInside(insidegrid[:,:3],-A/2.,R1),3]=b1
         insidegrid[isInside(insidegrid[:,:3],A/2.,R2),3]=b2
         # and maybe a mix ; this depends on your model
         insidegrid[isInside(insidegrid[:,:3],-A/2.,R1) & isInside(insidegrid[:,:3],A/2.,R2),3]=(b2+b1)/2.
         # calc the scattering
         result=js.ff.cloudScattering(q,insidegrid,nFib=nFib)
         result.Y=result.Y+bgr
         # add attributes for later usage
         result.A=A
         result.R1=R1
         result.R2=R2
         result.dx=dx
         result.insidegrid=insidegrid
         return result
     #
     # test it
     q=np.r_[0.01:10:0.02]
     data=dumbbell(q,4,2,2,0.5,1.5)
     # show result configuration
     js.mpl.scatter3d(data.insidegrid[:,0],data.insidegrid[:,1],data.insidegrid[:,2])
     #
     # Fit your data like this (I know that b1 abd b2 are wrong).
     # It may be a good idea to use not the highest resolution in the beginning because of speed.
     # If you have a good set of starting parameters you can decrease dx.
     data2=data.prune(number=100)
     data2.makeErrPlot(yscale='l')
     data2.fit(model=dumbbell,
         freepar={'A':3},
         fixpar={'R1':2,'R2':2,'dx':0.3,'b1':1,'b2':2,'bgr':0},
         mapNames={'q':'X'})



    References
    ----------
    .. [1] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1
    .. [2] An improved method for calculating the contribution of solvent to the X-ray diffraction pattern of biological molecules
           Fraser R MacRae T Suzuki E IUCr Journal of Applied Crystallography 1978 vol: 11 (6) pp: 693-694
    .. [3] X-ray diffuse scattering by proteins in solution. Consideration of solvent influence
           B. A. Fedorov, O. B. Ptitsyn and L. A. Voronin J. Appl. Cryst. (1974). 7, 181-186 doi: 10.1107/S0021889874009137
    """

    if cloud.shape[1]==4:
        # last colum is scattering length
        blength=cloud[:,3]
        cloud=cloud[:,:3]
    else:
        blength=np.ones(cloud.shape[0])
    sumblength=blength.sum()
    if nFib==0:
        result=dA(np.c_[q,[_scattering_Debye(cloud,blength,qx)/sumblength**2 for qx in q] ].T)
        result.sumblength=sumblength
        result.setColumnIndex(iey=None)
        result.columnname='q; Pq'
    elif nFib>0:
        if isinstance(formfactor,str):
            if formfactor.startswith('g'):
                # gaussian shape
                formfactoramp=np.c_[q,np.exp(-q**2*V**(2/3.)/4./np.pi)].T
                formfactor='gaussian'
            elif formfactor.startswith('s'):
                # sphere
                R=(3.*V/4./np.pi)**(1/3.)
                formfactoramp=np.c_[q,_fa_sphere(q*R)].T
                formfactor = 'sphere'
        elif isinstance( formfactor,np.ndarray):
            formfactoramp=np.c_[formfactor[0],formfactor[1]**0.5/formfactor[1,0]**0.5].T
            formfactor='explicit'
        else:
            # const form factor as default
            formfactoramp=np.c_[q,np.ones_like(q)].T
            formfactor = 'constant'
        res=parallel.doForList(formel.sphereAverage,q,
                 _scattering,r=cloud,blength=blength,formfactor=formfactoramp,rms=rms,ffpolydispersity=ffpolydispersity,
                 ncpu=ncpu,relError=nFib,loopover='q',output=False)
        res=np.array(res).T
        # the third row is F(Q) but will be parameter beta according to Chen
        #  which is beta=|<F(Q)>|²/<|F(Q)|²>   and scattering amplitude F(Q)
        res[2]=(res[2]*res[2].conj())/res[1]
        res[1]/=sumblength**2
        result=dA(res[:3],dtype=np.float)
        result.sumblength=sumblength
        result.formfactoramplitude_q=formfactoramp[0]
        result.formfactoramplitude = formfactoramp[1]
        result.formfactor = formfactor
        result.rms=rms
        result.ffpolydispersity=ffpolydispersity
        result.setColumnIndex(iey=None)
        result.columnname='q; Pq; beta'
    return result

def _coneAverage(qlist,qxz,qrpt,qfib,r,blength,formfactor,rms):
    q,ilist=qlist                           # ilist is index in qxz of the qxz with same q value
    fa = blength * np.interp(q, formfactor[0, :], formfactor[1, :])
    qfib[:,0]=q                             # cone points around [0,0,1] direction
    fibpoints=formel.rphitheta2xyz(qfib)    # cartesian coordinates of fibonacci lattice with radius q
    # do the average for all in ilist
    res={}
    pi_2=np.pi/2
    for il in ilist:
        # get angles
        _,p,t=qrpt[il]
        # rotate fibpoints to angles
        R=formel.rotationMatrix(formel.rphitheta2xyz(np.r_[1,p-pi_2,pi_2]),t)
        Rfibpoints=np.einsum('ij,jk->ki',R,fibpoints.T)
        # take mean of rotated fibpoints
        res[il]=np.mean([_sqx(point,r,fa,rms) for point in Rfibpoints])
    return res

def _coneAverage2(qlist,ca,qxz,nCone,r,blength,formfactor,rms):
    """
    unused function !!!!!!!!
    Idea use the same fibonacci lattice and save time from overlapping points (save calculation time)
    saves only 20% in cpu time on 6 cores compared to _coneAverage, but makes the code unclear.
    Only still here for documentation

    call by
    res = parallel.doForList(_coneAverage2, qlist,
                                 ca=coneangle,qxz=qxz, nCone=nCone, r=cloud, blength=blength, formfactor=formfactoramp,
                                 rms=rms,
                                 ncpu=ncpu, loopover='qlist', output=False)
    """


    q,ilist=qlist                      # ilist is index in qxz of the qxz with same q value
    fa = blength * np.interp(q, formfactor[0, :], formfactor[1, :])

    # fraction of sphere surface in cone to get NN points in coneangle
    ca = np.deg2rad(ca)
    surffraction=(2*np.sin(ca)**2+(1-np.cos(ca))**2)/4
    qfib=formel.fibonacciLatticePointsOnSphere(np.trunc(nCone/2./surffraction),r=1)
    nfib=formel.rphitheta2xyz(qfib)
    qfib[:,0]=q                   # cartesian coordinates of fibonacci lattice with radius q
    fibpoints=formel.rphitheta2xyz(qfib)
    # precalc what is needed
    il=ilist[0]
    needed=[np.arccos(np.einsum('i,ji',qxz[il],nfib)/np.linalg.norm(qxz[il]))<ca for il in ilist]
    sq = np.r_[[_sqx(point,r,fa,rms) if sel else -1 for point,sel in zip(fibpoints,np.logical_or.reduce(needed,axis=0)) ]]
    res={}
    for il,ne in zip(ilist,needed):
        # take mean of rotated fibpoints
        res[il]=np.mean(sq[ne])
    return res

def _sqx(qx,r,fa,rms=0):
    """
    coherent scattering of equal objects at positions r in direction point on
    sphere with length (radius) q

    Parameters
    ----------
    qx :  array 3 x 1
        point on unit sphere within oriented cone
    r : array  N x 3
        vector of objekt positions
    fa : float
        blength*formfactor(q)
    rms : float
        < random displacements >

    Returns
    -------
    F(Q)*F(Q).conj()

    pure numpy way
    """
    if rms>0:
        r=r+np.random.randn(r.shape[0],3)*rms
    iqr=np.einsum('i,ji',qx,r)*1j
    beiqrsum=np.einsum('i,i',fa,np.exp(iqr))
    Sq=beiqrsum*beiqrsum.conj()
    return Sq.real

def orientedCloudScattering(qxz, cloud, rms=0, coneangle=10, nCone=50, V=0, formfactor=None, ncpu=0):
    r"""
    2D scattering of an oriented cloud of scatterers with equal or variable scattering length. Using multiprocessing.

    Cloud can represent an object described by a cloud of isotropic scatterers with orientation averaged in a cone.
    Scattering amplitudes may be constant, sphere scattering amplitude, Gaussian scattering amplitude
    or explicitly given form factor. Rememeber that the atomic bond length are on the order 0.1-0.2 nm
    and one expects Bragg peaks.

    Parameters
    ----------
    qxz : array, ndim= Nx3
         wavevectors in 1/nm
    cloud : array Nx3 or Nx4
        - Center of mass positions (in nm) of the N scatterers in the cloud.
        - If given cloud[3] is the scattering length :math:`b` at positions cloud[:3], otherwise :math:`b=1`.
    coneangle : float
        Coneangle in units degrees.
    rms : float, default=0
        Root mean square displacement =<u**2>**0.5 of the positions in cloud as random (Gaussian) displacements in units nm.
        Dispacement u is random for each orientation nCone.
        rms can be used to simulate a Debye-Waller factor. Larger nCone is advised to smooth data.
    nCone : int
        Cone average as average over nCone Fibonacci lattice points in cone.
    V : float, default=0
        Volume of the scatterers for formfactor 'gauss' and 'sphere'.
    formfactor : 'gauss','sphere',array 2xN,default=None
        Gridpoint scattering amplitudes are described by:
         - None    : const scattering amplitude, point like particle.
         - 'sphere': Sphere scattering amplitude according to [3]_. The sphere radius is :math:`R=(\\frac{3V}{4\\pi})^{1/3}`
         - 'gauss' : Gaussian function :math:`b_i(q)=bVexp(- \\frac{V^{2/3.}}{4\pi}q^2)` according to [2]_.
         - explicit isotropic form factor ff as array with [q,ff] e.g. from multishell.
           The normalized scattering amplitude fa for each gridpoint is calculated as fa=ff**0.5/fa(0).
           Missing values are linear intepolated (np.interp), q values outside interval are mapped to qmin or qmax.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
         - not given or 0 : all cpus are used
         - int>0          : min(ncpu, mp.cpu_count)
         - int<0          : ncpu not to use
         - 1              : single core usage for testing or comparing speed to Debye

    Returns
    -------
        dataArray [qx,qz, Pq]
         - The forward scattering is Pq(q=0)= sumblength**2
         - .sumblength : Sum of blength with sumblength**2
         - .formfactoramplitude : formfactoramplitude of cloudpoints according to type for all q values.
         - .formfactoramplitude_q :corresponding q values.

    Examples
    --------
    How to use orientedCloudScattering for fitting see last Example in cloudScattering.

    ::

     import jscatter as js
     import numpy as np
     # two points along y result in pattern independent of x but cos**2 for z
     # with larger coneangle Ix becomes qx dependent
     rod0=np.zeros([2,3])
     rod0[:,1]=np.r_[0,np.pi]
     qxz=np.mgrid[-6:6:50j, -6:6:50j].reshape(2,-1).T
     ffe=js.ff.orientedCloudScattering(qxz,rod0,coneangle=5,nCone=10,rms=0)
     fig=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     fig.axes[0].set_title(r'cos**2 for Z and slow decay for X due to 5 degree cone')
     fig.show()
     # noise in positions
     ffe=js.ff.orientedCloudScattering(qxz,rod0,coneangle=5,nCone=100,rms=0.1)
     fig=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     fig.axes[0].set_title('cos**2 for Y and slow decay for X with position noise')
     fig.show()
     #
     # two points along z result in symmetric pattern around zero
     # asymetry reflects fibonacci lattice -> increase nCone
     rod0=np.zeros([2,3])
     rod0[:,2]=np.r_[0,np.pi]
     ffe=js.ff.orientedCloudScattering(qxz,rod0,coneangle=45,nCone=10,rms=0.005)
     fig2=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     fig2.axes[0].set_title('symmetric because of orientation along z; \n nCone needs to be larger for large cones')
     fig2.show()
     #
     # 5 spheres in line with small position distortion
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     qxz = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
     ffe = js.ff.orientedCloudScattering(qxz, rod0, formfactor='sphere', V=4/3.*np.pi*2**3, coneangle=20, nCone=30, rms=0.02)
     fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
     fig4.axes[0].set_title('5 spheres with R=2 along Z with noise (rms=0.02)')
     fig4.show()
     #
     # 5 core shell particles in line with small position distortion (Gaussian)
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     qxz = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
     # only as demo : extract q from qxz
     qxzy = np.c_[qxz, np.zeros_like(qxz[:, 0])]
     qrpt = js.formel.xyz2rphitheta(qxzy)
     q = np.unique(sorted(qrpt[:, 0]))
     # or use interpolation
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)
     ffe = js.ff.orientedCloudScattering(qxz, rod0, formfactor=cs, coneangle=20, nCone=100, rms=0.05)
     fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
     fig4.axes[0].set_title('5 core shell particles with R=2 along Z with noise (rms=0.05)')
     fig4.show()

    Make a slice for an angular region but with higher resolution to see the additional peaks due to allignement
    ::

     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     qxz = np.mgrid[-4:4:150j, -4:4:150j].reshape(2, -1).T
     # only as demo : extract q from qxz
     qxzy = np.c_[qxz, np.zeros_like(qxz[:, 0])]
     qrpt = js.formel.xyz2rphitheta(qxzy)
     q = np.unique(sorted(qrpt[:, 0]))
     # or use interpolation
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)
     ffe = js.ff.orientedCloudScattering(qxz, rod0, formfactor=cs, coneangle=20, nCone=100, rms=0.05)
     fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
     fig4.axes[0].set_title('5 core shell particles with R=2 along Z with noise (rms=0.05)')
     fig4.show()
     #
     # transform X,Z to spherical coordinates
     qphi=js.formel.xyz2rphitheta([ffe.X,ffe.Z,abs(ffe.X*0)],transpose=True )[:,:2]
     # add qphi or use later rp[1] for selection
     ffb=ffe.addColumn(2,qphi.T)
     # select a portion of the phi angles
     phi=np.pi/2
     dphi=0.2
     ffn=ffb[:,(ffb[-1]<phi+dphi)&(ffb[-1]>phi-dphi)]
     ffn.isort(-2)    # sort along radial q
     p=js.grace()
     p.plot(ffn[-2],ffn.Y,le='oriented spheres form factor')
     # compare to coreshell formfactor scaled
     p.plot(cs.X,cs.Y/cs.Y[0]*25,li=1,le='coreshell form factor')
     p.yaxis(label='F(Q,phi=90°+-11°)', scale='log')
     p.title('5 alligned core shell particle with additional interferences',size=1.)
     p.subtitle(' due to sphere allignement dependent on observation angle')

     # 2: direct way with 2D q in xz plane
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     x=np.r_[0.0:6:0.05]
     qxzy = np.c_[x, x*0,x*0]
     for alpha in np.r_[0:91:30]:
         R=js.formel.rotationMatrix(np.r_[0,0,1],np.deg2rad(alpha)) # rotate around Z axis
         qa=np.dot(R,qxzy.T).T[:,:2]
         ffe = js.ff.orientedCloudScattering(qa, rod0, formfactor=cs, coneangle=20, nCone=100, rms=0.05)
         p.plot(x,ffe.Y,li=[1,2,-1],sy=0,le='alpha=%g' %alpha)
     p.xaxis(label=r'Q / nm\S-1')
     p.legend()

    """
    nCone = max(10, nCone)
    # make 3D q with qz=0
    qxz=np.c_[qxz, np.zeros_like(qxz[:, 0])]
    if cloud.shape[1]==4:
        # last colum is scattering length
        blength=cloud[:,3]
        cloud=cloud[:,:3]
    else:
        blength=np.ones(cloud.shape[0])
    sumblength=blength.sum()

    # cone to average  which is around Z direction = [0,0,1]xyz = [1,0,0]rpt
    qfib=formel.fibonacciLatticePointsOnSphere(nCone,1)
    qfib=qfib[qfib[:,2]<np.pi/2,:]           # select half sphere
    qfib[:,2]*=(coneangle/90.)               # shrink to cone

    # transform to spherical coordinates and make selective qlist
    qrpt=formel.xyz2rphitheta(qxz)
    qround=np.round(qrpt[:,0],3)
    qred=np.unique(qround)                               # reduced q list list to 10**-3 precision
    qlist=[(qi,np.where(qround==qi)[0]) for qi in qred]  # list of qred with original Q indices

    # define formfactor for qround
    if isinstance(formfactor,str):
        if formfactor.startswith('g'):
            # gaussian shape
            formfactoramp=np.c_[qred,np.exp(-qred**2*V**(2/3.)/4./np.pi)].T
            formfactor='gaussian'
        elif formfactor.startswith('s'):
            # sphere
            R=(3.*V/4./np.pi)**(1/3.)
            formfactoramp=np.c_[qred,_fa_sphere(qred*R)].T
            formfactor = 'sphere'
    elif isinstance( formfactor,np.ndarray):
        formfactoramp=np.c_[formfactor[0],formfactor[1]**0.5/formfactor[1,0]**0.5].T
        formfactor='explicit'
    else:
        # const form factor as default
        formfactoramp=np.c_[qred,np.ones_like(qred)].T
        formfactor = 'constant'

    # do in parallel for all q rings
    res=parallel.doForList(_coneAverage,qlist,
                           qxz=qxz,qrpt=qrpt,qfib=qfib,r=cloud,blength=blength,formfactor=formfactoramp,rms=rms,
                           ncpu=ncpu,loopover='qlist',output=False)

    # distribute Sxy according to saved indices from qlist
    for res1 in res:
        for ii,Sxy in res1.items():
            qxz[ii, 2]= Sxy
    result=dA(qxz.T[:3], dtype=np.float)
    result.sumblength=sumblength
    result.formfactoramplitude_q=formfactoramp[0]
    result.formfactoramplitude = formfactoramp[1]
    result.formfactortype=formfactor
    if V>0:
        result.Volume=V
    result.setColumnIndex(ix=0,iy=2,iz=1,iey=None)
    result.columnname='qx; qz; Pq'
    return result

def pearlNecklace(Q,Rc,l,N,A1=None,A2=None,A3=None,ms=None,mr=None):
    """
    Formfactor of a pearlnecklace (freely jointed chain of pearls connected by rods)

    The formfactor is normalized that the pearls contribution equals 1.

    Parameters
    ----------
    Q : array
        wavevector in nm
    Rc : float
        pearl radius in nm
    N : float
        number of pearls (homogeneous spheres)
    l : float
        physical length of the rods
    A1, A2, A3 : float
        Amplitudes of pearl-pearl, rod-rod and pearl-rod scattering.
        Can be calculated with the number of chemical monomers in a pearl ms and rod mr (see below for further information)
        If ms and mr are given A1,A2,A3 are calculated from these.
    ms : float, default None
        number of chemical monomers in each pearl
    mr : float, default None
        number of chemical monomers in rod like strings

    Returns
    -------
    dataarray [q, Iq]
    .pearlRadius
    .A1
    .A2
    .A3
    .numberPearls
    .mr
    .ms
    .stringLength

    Notes
    -----
     - M : number of rod like strings (M=N-1)
     - A1 = ms²/(M*mr+N*ms)²
     - A2 = mr²/(M*mr+N*ms)²
     - A3 = (mr*ms)/(M*mr+N*ms)²

    References
    ----------
    .. [1] R. Schweins, K. Huber, Macromol. Symp., 211, 25-42, 2004.


    """
    #written by L. S. Fruhner, FZJ Juelich 2016
    N=np.float(N) #always float
    if ms is not None and mr is not None:
        try:
            M=N-1
            A1 = ms**2/(M*mr+N*ms)**2
            A2 = mr**2/(M*mr+N*ms)**2
            A3 = (mr*ms)/(M*mr+N*ms)**2
        except:
            raise ValueError('ms and mr should be given as float')
    Y1=3*(np.sin(Q*Rc)-(Q*Rc)*np.cos(Q*Rc))/(Q*Rc)**3
    Z1=2*Y1**2*(N/(1-np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))-N/2-(1-(np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))**N)/(1-np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))**2*np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))
    B=special.sici(Q*l) [0]
    Y2=B/(Q*l)
    C=special.sici(Q*((l+2*Rc)-Rc))[0]
    D=special.sici(Q*Rc)[0]
    Y3=(C-D)/(Q*l)
    Z2=(N-1)*(2*Y2-(np.sin(Q*l/2)/(Q*l/2))**2)+2*(N-1)*Y3**2/(1-np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))-2*Y3**2*(1-(np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))**(N-1)/(1-np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))**2)
    Z3=Y3*Y1*4*((N-1)/(1-np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))-(1-(np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))**(N-1))/(1-np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))**2*np.sin(Q*(l+2*Rc))/(Q*(l+2*Rc)))
    # add the different contributions
    YY=A1*Z1+A2*Z2+A3*Z3
    result=dA(np.c_[Q,YY].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Fq'
    result.pearlRadius=Rc
    result.A1=A1
    result.A2=A2
    result.A3=A3
    result.numberPearls=N
    result.mr=mr
    result.ms=ms
    result.stringLength=l
    return result

def ellipsoid(q,Ra,Rb,SLD=1,solventSLD=0,alpha=[0,90],tol=1e-6,beta=False):
    """
    Form factor for a simple ellipsoid (ellipsoid of revolution).
    
    Parameters
    ----------
    q : float
        scattering vector unit e.g.  1/A or 1/nm  1/Ra
    Ra : float
        radius rotation axis   units in 1/unit(q)
    Rb : float 
        radius rotated axis    units in 1/unit(q)
    SLD : float, default =1
        Scattering length density of unit nm^-2
        e.g. SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2 for neutrons
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
        e.g. D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2 for neutrons
    alpha : [float,float] , default [0,90]
        alpha is angle between rotation axis Ra and scattering vector q in unit grad
        between these angles orientation is averaged
        alpha=0 axis and q are parallel, other orientation is averaged
    beta : True,default False
        beta is asymmetry factor according to [3]_.
        beta = |<F(Q)>|²/<|F(Q)|²> with scattering amplitude F(Q) and form factor P(Q)=<|F(Q)|²>
    tol : float
        relative tolerance for integration between alpha

    Returns
    -------
    dataArray with columns [q; Iq; beta ] # if beta=True
    .RotationAxisRadius
    .RotatedAxisRadius
    .EllipsoidVolume
    .I0         forward scattering q=0

    References
    ----------
    .. [1] Structure Analysis by Small-Angle X-Ray and Neutron Scattering
           Feigin, L. A, and D. I. Svergun, Plenum Press, New York, (1987).
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Ellipsoid.html
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    contrast=SLD-solventSLD
    result=multiShellEllipsoid(q,Ra,Rb,shellSLD=SLD,solventSLD=solventSLD,alpha=alpha,tol=tol)
    attr=result.attr
    result.EllipsoidVolume=result.outerVolume
    result.RotationAxisRadius=Ra
    result.RotatedAxisRadius=Rb
    result.contrast=result.shellcontrast
    result.angles=alpha
    attr.remove('columnname')
    for at in attr:
        delattr(result,at)
    result.modelname=sys._getframe().f_code.co_name
    return result

def multiShellEllipsoid(q,poleshells,equatorshells,shellSLD,solventSLD=0,alpha=[0,90],tol=1e-6):
    """
    Scattering of multi shell ellipsoidal particle with variing shell thickness at pole and equator.

    Shell thicknesses add up to form complex particles with any combination of axial ratios and shell thickness.
    A const axial ratio means different shell thickness at equator and pole.

    Parameters
    ----------
    q : array
        Wavevectors, unit 1/nm
    equatorshells : list of float
        Thickness of shells starting from inner most for rotated axis Re making the equator. unit nm.
        The absolute values are used.
    poleshells : list of float
        Thickness of shells starting from inner most for rotating axis Rp pointing to pole. unit nm.
        The absolute values are used.
    shellSLD : list of float
        List of scattering length densities of the shells in sequence corresponding to shellthickness. unit nm^-2.
    solventSLD : float, default=0
        Scattering length density of the surrounding solvent. unit nm^-2

    Returns
    -------
    dataArray [q, Iq]
    Iq,                    scattering cross section in units nm**2
    .contrastprofile       as radius and contrast values at edge points of equatorshells
    .equatorshellthicknes  consecutive shell thickness
    .poleshellthickness
    .shellcontrast         contrast of the shells to the solvent
    .equatorshellradii     outer radius of the shells
    .poleshellradii
    .outerVolume           Volume of complete sphere
    .I0                    forward scattering for Q=0

    Examples
    --------
    Simple ellipsoid in vacuum::

     x=np.r_[0.0:10:0.01]
     Rp=2.
     Re=1.
     ashell=js.ff.multiShellEllipsoid(x,Rp,Re,1)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(ashell)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs

    Alternating shells with thickness 0.3 nm h2o and 0.2 nm d2o in vacuum::

     x=np.r_[0.0:10:0.01]
     shell=np.r_[[0.3,0.2]*3]
     sld=[-0.56e-4,6.39e-4]*3
     # constant axial ratio for all shells but nonconstant shell thickness
     axialratio=2
     ashell=js.ff.multiShellEllipsoid(x,axialratio*shell,shell,sld)
     # shell with constant shellthickness of one component and other const axialratio
     pshell=shell[:]
     pshell[0]=shell[0]*axialratio
     pshell[2]=shell[2]*axialratio
     pshell[4]=shell[4]*axialratio
     bshell=js.ff.multiShellEllipsoid(x,pshell,shell,sld)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(ashell,le='const. axial ratio')
     p[1].plot(ashell.contrastprofile,li=2) # a contour of the SLDs
     p[0].plot(bshell,le='const shell thickness')
     p[1].plot(bshell.contrastprofile,li=2) # a contour of the SLDs
     p[0].legend()

    double shell with exponential decreasing exterior shell to solvent scattering::

     x=np.r_[0.0:10:0.01]
     def doubleexpshells(q,d1,ax,d2,e3,sd1,sd2,sol):
        shells =[d1   ,d2]+[e3]*9
        shellsp=[d1*ax,d2]+[e3]*9
        sld=[sd1,sd2]+list(((sd2-sol)*np.exp(-np.r_[0:3:9j])))
        return js.ff.multiShellEllipsoid(q,shellsp,shells,sld,solventSLD=sol)
     dde=doubleexpshells(x,0.5,1,0.5,1,1e-4,2e-4,0)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(dde)
     p[1].plot(dde.contrastprofile,li=1) # a countour of the SLDs

    References
    ----------
    .. [1] Structure Analysis by Small-Angle X-Ray and Neutron Scattering
           Feigin, L. A, and D. I. Svergun, Plenum Press, New York, (1987).
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Ellipsoid.html
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    if isinstance(shellSLD,      (float,int)): shellSLD=[shellSLD]
    if isinstance(poleshells,    (float,int)): poleshells=[poleshells]
    if isinstance(equatorshells, (float,int)): equatorshells = [equatorshells]
    if len(shellSLD)!=len(equatorshells) or len(equatorshells)!=len(poleshells):
        raise Exception(
            'shellSLD and equatorshells should be of same length but got:%i!=%i'%(len(shellSLD),len(equatorshells)))
    alpha = np.deg2rad(alpha)/np.deg2rad(90)        # set alpha so [0,1] interval which is [0,90]
    requ  = np.cumsum(np.abs(equatorshells))           # returns array with absolute values
    rpol  = np.cumsum(np.abs(poleshells))
    dSLDs = np.r_[shellSLD]-solventSLD              # subtract solvent to have in any case the contrast to the solvent

    # forward scattering Q=0 -------------
    Vr=4/3.*np.pi*requ**2*rpol
    dslds=Vr*dSLDs
    dslds[:-1]=dslds[:-1]-Vr[:-1]*dSLDs[1:]         # subtract inner shell
    fa0=dslds.sum()

    # scattering amplitude in general
    def _ellipsoid_ffamp(Q,x,Re,Rp):
        axialratio = Rp / Re
        z = lambda q, Re, x: q * Re * np.sqrt(1 + x ** 2 * (axialratio ** 2 - 1))
        f = lambda z: 3 * (np.sin(z) - z * np.cos(z)) / z ** 3
        return f(z(Q, Re, x))

    def _ffa(q,x,re,rp):
        # avoid zero
        Q = np.where(q == 0, q * 0 + 1e-10, q)
        # scattering amplitude multishell Q and R are column and row vectors
        # outer shell radius
        fa=Vr*dSLDs*_ellipsoid_ffamp(Q[:,None],x,re,rp)
        if len(re)>1:
            # subtract inner radius for multishell, innermost shell has r=0
            fa[:,1:]=fa[:,1:]-Vr[:-1]*dSLDs[1:]*_ellipsoid_ffamp(Q[:,None],x,re[:-1],rp[:-1])
        # sum over radii and square for intensity
        fa=fa.sum(axis=1)
        # restore zero
        Fa= np.where(q == 0, fa0, fa)
        Fq= Fa**2
        # return scattering intensity and scattering amplitude for beta
        return np.c_[Fq, Fa]

    # integration over orientations for all q
    res = formel.parQuadratureAdaptiveGauss(_ffa,alpha[0],alpha[1],'x',tol=tol,miniter=30,q=q,re=requ,rp=rpol)
    # calc beta
    res[1]=res[1]**2/res[0]
    result=dA(np.c_[q,res.T].T)
    result.setColumnIndex(iey=None)
    result.columnname='q; Iq; beta'
    result.equatorshellsthickness=equatorshells
    result.poleshellthickness=poleshells
    result.shellcontrast=shellSLD
    result.equatorshellradii=requ
    result.poleshellradii   =rpol
    contrastprofile=np.c_[np.r_[requ-equatorshells,requ],np.r_[shellSLD,shellSLD]].T
    result.contrastprofile=contrastprofile[:,np.repeat(np.arange(len(shellSLD)),2)+np.tile(np.r_[0,len(shellSLD)],len(shellSLD))]
    result.outerVolume=4./3*np.pi*max(requ)**2*max(rpol)
    result.I0=fa0**2
    result.modelname=sys._getframe().f_code.co_name
    return result

def _ellipsoid_ff_amplitude(q,x,Ra,Rb):
    """
    Ellipsoidal formfator amplitude for internal usage only. save for q=0
    q in nm
    x in rad
    Ra,Rb in nm

    If x is an array of len N the outout is shape N+1,len(q) with 0 as q and 1:N+1 as result

    """
    Q = np.where(q == 0, q * 0 + 1e-10, q)
    nu = Ra / float(Rb)
    z = lambda q, Rb, x: q[:,None] * Rb * np.sqrt(1 + x ** 2 * (nu ** 2 - 1))
    f = lambda z: 3 * (np.sin(z) - z * np.cos(z)) / z ** 3
    fa=f(z(Q, Rb, x))
    fa= np.where(q[:,None] == 0, 1, fa)
    return dA(np.c_[q, fa].T)

def ellipsoidFilledCylinder(q=1,R=10,L=0,Ra=1,Rb=2,eta=0.1,SLDcylinder=0.1,SLDellipsoid=1,SLDmatrix=0,alpha=90,epsilon=[0,90],fPY=1,dim=3):
    """
    Scattering of a cylinder filled with ellipsoidal particles.

    Ellipsoids of revolution with a fluid like distribution and hard core interaction leading to Percus-Yevick structure
    factor between ellipsoids. Ellipsoids can be oriented along cylinder axis.
    If cylinders are in a lattice, the .Y component is seen in the diffusive scattering and  the dominating
    cylinder contributes only to the bragg peaks.

    Parameters
    ----------
    q : array
        wavevectors in units 1/nm
    R : float
        Cylinder radius in nm
    L : float
        Length of the cylinder in nm
        If zero infinite length is assumed, but absolute intensity is not valid, only relative intensity.
    Ra : float
        radius rotation axis   units in nm
    Rb : float
        radius rotated axis    units in nm
    eta : float
        Volume fraction of ellipsoids in cylinder for use in PercusYevick structure factor.
        Radius in PY corresponds to sphere with same Volume as the ellipsoid.
    SLDcylinder : float,default 1
        Scattering length density cylinder material in nm**-2
    SLDellipsoid : float,default 1
        Scattering length density of ellipsoids in cylinder in nm**-2
    SLDmatrix : float
        Scattering length desnity of the matrix outside the cylinder in nm**-2
    alpha : float, default 90
        orientation of the cylinder axis to wavevector in degrees
    epsilon : [float,float], default [0,90]
        min,max orientations of ellipsoids rotation axis relative to cylinder axis in degrees
    fPY : float
        Factor between radius of ellipsoids Rv (equivalent volume) and radius used in structure factor Rpy
        Rpy=fPY*(Ra*Rb*Rb)**(1/3)
    dim : 3,1, default 3
        Dimensionality of the PercusYevick structure factor
        1 is one dimensional stricture factor, anything else is 3 dimesional (normal PY)

    Returns
    -------
    dataArray [q,n*conv ellipsoids + cylinder, n *conv ellipsoids, cylinder, n * ellipsoids , structure factor, beta ellipsoids ]
        Each contributing formfactor is given with its absolute contribution V**2*contrast**2 (NOT normalized to 1)
        beta ellipsoids is the asymmetry factor of Chen and Kotlarchyk.

    Examples
    --------
    ::

     import jscatter as js
     p=js.grace()
     q=js.loglist(0.01,5,800)
     ff=js.ff.ellipsoidFilledCylinder(q,L=100,R=5,Ra=2,Rb=1.5,eta=0.4,alpha=90,epsilon=[0,90])
     p.plot(ff.X,ff[2],legend='convolution cylinder x ellipsoids')
     p.plot(ff.X,ff[3],legend='cylinder only')
     p.plot(ff.X,ff[4],legend='ellipsoid only')
     p.plot(ff.X,ff[5],legend='structure factor ellipsoids')
     p.plot(ff.X,ff.Y,legend='conv. ellipsoid + filled cylinder')
     p.legend()
     p.yaxis(scale='l',label='I(q)')
     p.xaxis(scale='l',label='q / nm\S-1')

     # an angular averaged formfactor
     def averageEFC(q,R,L,Ra,Rb,eta,alpha=[alpha0,alpha1],fPY=fPY)
         res=js.dL()
         alphas=np.deg2rad(np.r_[alpha0:alpha1:13j])
         for alpha in alphas:
             ffe=js.ff.ellipsoidFilledCylinder(q,R=R,L=L,Ra=Ra,Rb=Rb,eta=ata,alpha=alpha,)
             res.append(ffe)
         result=res[0].copy()
         result.Y=scipy.integrate.simps(res.Y,alphas)/(alpha1-alpha0)
         return result

    References
    ----------
    to be published

    """
    q=np.atleast_1d(q)
    sldc=SLDmatrix-SLDcylinder
    slde=SLDellipsoid-SLDcylinder
    alpha=np.deg2rad(np.r_[alpha])
    epsilon=np.deg2rad(epsilon)/np.deg2rad(90)
    Ra=abs(Ra)
    Rb=abs(Rb)

    nu=Ra/float(Rb)
    Vell = 4*np.pi/3.*Ra*Rb*Rb
    if L==0:
        Vcyl=np.pi*R**2*1
    else:
        Vcyl=np.pi*R**2*L
    # matrix with q and x for later integration
    Rge=(Ra**2+2*Rb**2)**0.5
    RgL=(R**2/2.+L**2/12)**0.5
    # catch if really low Q are tried
    lowerlimit=min(0.01/Rge,min(q)/5.)
    upperlimit=min(100/Rge,max(q)*5.)
    qq = np.r_[0,formel.loglist(lowerlimit,upperlimit,200)]
    #width dq between Q values for integration;
    dq=qq*0
    dq[1:]=((qq[1:]-qq[:-1])/2.)
    dq[0]=(qq[1]-qq[0])/2.          #above zero
    dq[-1]=qq[-1]-qq[-2]           #asume extend to inf

    # generate ellipsoid orientations
    points=formel.fibonacciLatticePointsOnSphere(1000)
    pp= points[(points[:,2]>epsilon[0]) & (points[:,2]<epsilon[1])]
    v=formel.rphitheta2xyz(pp)
    #assume cylinder axis as [0,0,1], rotate the ellipsoid distribution to alpha cylinder axis around [1,0,0]
    RotM=formel.rotationMatrix([1,0,0],alpha)
    pxyz=np.dot(RotM,v.T).T
    #points in polar coordinates still with radius 1, thetha component is for average formfactor amplitude
    theta=formel.xyz2rphitheta(pxyz)[:,2]
     # use symmetry of _ellipsoid_ff_amplitude
    theta[theta>np.pi/2]=np.pi/2-theta[theta>np.pi/2]
    theta[theta<0]=-theta[theta<0]
    # get all ff_amplitudes interpolate and get mean
    eangles=np.r_[0:np.pi/2:45j]
    fee=_ellipsoid_ff_amplitude(qq,eangles/np.deg2rad(90),Ra,Rb)[1:].T
    feei= scipy.interpolate.interp1d(eangles,fee)
    femean_qq=feei(theta).mean(axis=1)
    febetamean_qq=(feei(theta)**2).mean(axis=1)

    def _sfacylinder(q, R, L, angle):
        """
        single cylinder form factor amplitude for all angle
        q : wavevectors
        r : cylinder radius
        L : length of cylinder, L=0 is infinitly long cylinder
        angle : angle between axis and scattering vector q in rad
        for q<0 we get zero as a feature!!
        """
        # deal with possible zero in q and sin(angle)
        sina=np.sin(angle)
        qsina=q[:,None]*sina
        qsina[:,sina==0]=q[:,None]
        qsina[q==0,:]=1       # catch later
        result = np.zeros_like(qsina)
        if L > 0:
            qcosa=q[:,None]*np.cos(angle)
            fqq=lambda qsina,qcosa:2*special.j1(R*qsina)/(R*qsina)*special.j0(L/2.*qcosa)
            result[q>0,:] =fqq(qsina[q>0,:],qcosa[q>0,:])
            result[q==0,:] = 1
        else:
            fqq=lambda qsina: 2*special.j1(R * qsina) / (R * qsina)
            result[q>0,:] =fqq(qsina[q>0,:])
            result[q==0,:] = 1
        return result

    def fc2(q,R,L,angle):
        # formfactor cylinder ; this is squared!!!
        if angle[0]==angle[1]:
            res=_sfacylinder(q, R, L,np.r_[angle[0]])**2
        else:
            pj=(angle[1]-angle[0])//0.05
            if pj ==0:pj=2
            al_angle=np.r_[angle[0]:angle[1]:pj*1j]
            val=_sfacylinder(q, R, L,al_angle)
            res=np.trapz(val**2,al_angle,axis=1)
        return res

    def fefcconv(q,angle):
        # convolution of cylinder and ellipsoid;
        val=[(   femean_qq*_sfacylinder(q_-qq, R, L,np.r_[angle]).T[0]*dq).sum()/dq[qq<=q_].sum()  if q_>0 else 1 for q_ in qq]
        res=np.interp(q,qq,np.r_[val])
        return res

    # structure factor ellipsoids
    if dim==1:
        R1dim=(Ra*Rb*Rb)**(1/3.)
        Sq=sf.PercusYevick1D(q,fPY*R1dim,eta=fPY*eta)
        density=eta/(2*R1dim) # in unit 1/nm
    else:
        Sq=sf.PercusYevick(q,fPY*(Ra*Rb*Rb)**(1/3.),eta=fPY**3*eta)
        # particle number in cylinder volume
        density=Sq.molarity*constants.Avogadro/10e24   # unit 1/nm**3
    nV=density*Vcyl
    # contribution form factors
    ffellipsoids=nV*(slde*Vell)**2  *  np.interp(q,qq,femean_qq**2)
    ffellipsoidsbeta=np.interp(q,qq,(femean_qq**2/febetamean_qq))  # ala Kotlarchyk

    ffcylinder=   (sldc*Vcyl)**2    *  fc2(q,R,L, [alpha[0],alpha[0]])[:,0]
    # convoluted  form factor of ellipsoids
    if 0:
        # above some first minimum the ellipsoid beta is artificial high compared to proteins (potatoe like),
        #  this removes this if activated
        ffellipsoidsbeta[np.r_[False,ffellipsoidsbeta[1:]>ffellipsoidsbeta[0:-1]]]=0
        ffellipsoidsbeta[ffellipsoidsbeta.argmin():]=0
    # structure factor correction as in Chen, Kotlarchyk
    ffconv=nV*(slde*Vell)**2     *     fefcconv(q,alpha[0])**2 * (1+ffellipsoidsbeta*(Sq.Y-1))

    result=dA(np.c_[q, ffconv+ffcylinder, ffconv, ffcylinder, ffellipsoids, Sq.Y,ffellipsoidsbeta].T)
    result.cylinderRadius=R
    result.cylinderLength=L
    result.cylinderVolume=Vcyl
    result.ellipsoidRa=Ra
    result.ellipsoidRb=Rb
    result.ellipsoidRg=R
    result.ellipsoidVolume=Vell
    result.ellipsoidVolumefraction=eta
    result.ellipsoidNumberDensity=density  # unit 1/nm**3
    result.alpha=np.rad2deg(alpha[0])
    result.ellipdoidAxisOrientation=np.rad2deg(epsilon)
    result.setColumnIndex(iey=None)
    result.columnname='q; ellipsoidscylinder; ellipsoids; cylinder; nellipsoids; structurefactor; betaellipsoids'
    result.modelname=sys._getframe().f_code.co_name
    return result

def teubnerStrey(q,xi,d,eta2=1):
    """
    Phenomenological model for the scattering intensity of a two-component system using the Teubner-Strey model [1]_.

    Often used for  bi-continuous micro-emulsions.

    Parameters
    ----------
    q : array
        wavevectors
    xi : float
        correlation length
    d : float
        characteristic domain size, periodicity
    eta2 : float, default=1
        squared scattering length density contrast

    Returns
    -------
    dataArray [q, Iq]

    Notes
    -----
    - :math:`q_{max}=((2\pi/d)^2-\\xi^{-2})^{1/2}`

    Examples
    --------
    Fit Teubner-Strey with background and a power law for low Q
    ::
    
     #import jscatter as js
     #import numpy as np
    
     def tbpower(q,B,xi,dd,A,beta,bgr):
         # Model Teubner Strey  + power law and background
         tb=js.ff.teubnerStrey(q=q,xi=xi,d=dd)
         # add power law and background
         tb.Y=B*tb.Y+A*q**beta+bgr 
         tb.A=A
         tb.bgr=bgr
         tb.beta=beta
         return tb
    
     # simulate some data
     q=js.loglist(0.01,5,600)
     data=tbpower(q,1,10,20,0.002,-3,0.1)
     # or read them
     # data=js.dA('filename.chi')
    
     # plot data
     p=js.grace()
     p.plot(data,legend='simulated data')
     p.xaxis(scale='l',label=r'Q / nm\S-1')
     p.yaxis(scale='l',label='I(Q) / a.u.')
     p.title('TeubnerStrey model with power and background')



    References
    ----------
    .. [1] M. Teubner and R. Strey,
           Origin of the scattering peak in microemulsions,
           J. Chem. Phys., 87:3195, 1987
    .. [2] K. V. Schubert, R. Strey, S. R. Kline, and E. W. Kaler,
           Small angle neutron scattering near lifshitz lines: Transition from weakly structured mixtures to microemulsions,
           J. Chem. Phys., 101:5343, 1994

    """
    q=np.atleast_1d(q)
    qq=q*q
    k=2*np.pi/d
    a2=(k**2+xi**-2)**2
    b=k**2-xi**-2
    Iq=8*np.pi*eta2/xi/(a2-2*b*qq+qq*qq)
    result=dA(np.c_[q,Iq].T)
    result.correlationlength=xi
    result.domainsize=d
    result.SLD2=eta2
    result.setColumnIndex(iey=None)
    result.columnname='q; Iq'
    result.modelname=sys._getframe().f_code.co_name

    return result

def scatteringFromSizeDistribution(q,sizedistribution,fffunction=beaucage,fffkwargs={'G':1,'d':3},
                                   scatteringlength=lambda r:1):
    """
    Scattering of a size distribution of objects with form factor fffunction

    | scattering of a single size:
    | I(q) = n * drho^2 * V^2 * P(q)*S(q)
    | n       number density
    | drho    difference in scattering length density (contrast)
    | V       scattering Volume of particle ~r³ ~ mass
    | P(q)    formfactor with P(0)=1; here fffunction
    | S(q)    structure factor with S(inf)=>1 for simplicity
    |
    | size distribution
    | I(q)= sum_over_sizes[  scatteringlength(size) * probability(size) * fffunction(q,size,**fffkwargs).Y  ]  with S(q)=1

    Parameters
    ----------
    q : list/array of float; unit = 1/unit(size distribution)
        wavevectors to calculate scattering
    sizedistribution : dataArray or array
        distribution.T[i] should give pairs [size,probability,...]
        (X or dimension 0) -> list of sizes;
        (Y or dimension 1) list of probability
        eg. from DLS measurement
    fffunction : lambda or function
        function that describes the form factor like a beaucage (default)
        first arguments (q,R,...
        should return dataArray with .Y as result
    fffkwargs : args
        any additional keyword arguments for fffunction as dictionary
        eg. {'d':3}
    scatteringlength : function
        scattering_length(r)**2= drho**2 * V**2
        volume objects dimension 3 with scattering length density constant
        for number distribution:  scatteringlength per particle ~R**6
        for volume distribution:  scatteringlength per particle ~R**2  because V=r**3
        for intensity distribution:  scatteringlength per particle const  because V=r**3

    Returns
    -------
    dataArray [q,Iq or Fq]
    
    Notes
    -----
    To look at the contribution of aggregates of size 70 to 12 nm particles::

     # equal concentration
     p.plot(s.formel.scatteringFromSizeDistribution(s.loglist(0.01,6,100),[[12,70],[1,1]]),legend='with aggregates')
     # 2:1 concentration
     p.plot(s.formel.scatteringFromSizeDistribution(s.loglist(0.01,6,100),[[12,70],[2,1]]),legend='no aggregates')

    To look at a part of the distribution use sizedistribution.prune(min,max)

    If size,probability is not in column 0,1 use as for the Malvern frequencydistribution:
    sizedistribution=frequencydistribution[np.r_[4,1]]    if probability is column 1 and soze column 4

    It is instructive to plot the result together with  q*R~const
    p.plot(1/sizedistribution[0],sizedistribution[1])

    """
    sizedistribution=np.array(sizedistribution)
    result=[]
    for spr in sizedistribution.T:
        result.append(scatteringlength(spr[0])*spr[1]*fffunction(q,spr[0],**fffkwargs).Y)
    result=dA(np.c_[q,np.r_[result].sum(axis=0)].T)
    result.setColumnIndex(iey=None)
    result.formfactor=str(fffunction.__name__)
    result.formfactorkwargs=str(fffkwargs)
    result.modelname=inspect.currentframe().f_code.co_name
    return result

def superball(q,R,p,SLD=1,solventSLD=0,nGrid=15,returngrid=False):
    """
    A superball is a general mathematical shape that can be used to describe rounded cubes, sphere and octahedra.

    The numerical integration is done by a grid of scatterers, refined at the surface with an
    insidegrid and an outsidegrid averaged.

    Parameters
    ----------
    q : array
        Wavevector in 1/nm
    R : float, None
        2R = edge length
    p : float, 0<p<100
        parameter that descibes rounding
        | p=0       empty space
        | p<0.5     concave octahedra
        | p=0.5     octahedra
        | 0.5<p<1   convex octahedra
        | p=1       spheres
        | p>1       rounded cubes
        | p->inf    cubes
    SLD : float, default =1
        Scattering length density of cuboid.unit nm^-2
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
    nGrid : int
        Number of gridpoints in start lattice is nGrid**3. This is refined at the surface.til griddistance/3.
        nFib=nGrid*4 is used for Fibonacci lattice with 2*nFib+1 orientations in spherical average.

    Returns
    -------
        dataArray [q,Iq, beta]

    Notes
    -----
    For large Q we observe a peak corresponding to the grid that is used for the integration.
    This is a sign that the density of the grid is not high enough as we see something like internal grid structure.
    The same happens in standard integration routines if you integrate for the Q values with a fixed resolution.
    In these cases please choose a smaller grid and wait. :-)
    Use the time to think about the advantages of an analytical solution if it is availible and atomic resolution.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     #
     q=np.r_[0:5:0.02]
     R=6;
     p=js.grace()
     p.multi(2,1)
     p[0].yaxis(scale='l')
     ss=js.ff.superball(q,R,p=1,)
     p[0].plot(ss,legend='superball p=1')
     p[0].plot(js.ff.sphere(q,R),li=1,sy=0,legend='sphere ff')
     p[0].legend(x=1,y=1e-1)
     #
     p[1].yaxis(scale='l')
     cc=js.ff.superball(q,R,p=100)
     p[1].plot(cc,sy=[1,0.3,4],legend='superball p=100')
     p[1].plot(js.ff.cuboid(q,2*R),li=4,sy=0,legend='cuboid, but never reached')
     p[1].legend(x=1,y=1e6)
     p[1].text('internal structure of grid',x=3.5,y=4e4)
     #
     # visualisation
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     # cubic grid points
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     q=np.r_[0:5:0.1]
     R=3
     pxyz=js.ff.superball(q,R,p=200,nGrid=10,returngrid=True).grid
     pxyz=pxyz[pxyz[:,0]>0]
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-3,3])
     ax.set_ylim([-3,3])
     ax.set_zlim([-3,3])
     ax.set_aspect("equal")
     plt.tight_layout()
     plt.show(block=False)


    References
    ----------
    .. [1] Periodic lattices of arbitrary nano-objects: modeling and applications for self-assembled systems
           Yager, K.G.; Zhang, Y.; Lu, F.; Gang, O.
           Journal of Applied Crystallography 2014, 47, 118–129. doi: 10.1107/S160057671302832X
    .. [2] http://gisaxs.com/index.php/Form_Factor:Superball

    """
    alpha=np.pi/6. # rotation angle for grid
    p2=abs(2.*min(p,200.))
    R=abs(R)
    q=np.atleast_1d(q)
    contrast=SLD-solventSLD
    # volume according to Soft Matter, 2012, 8, 8826-8834, DOI: 10.1039/C2SM25813G
    V=8*R**3*special.gamma(1+1/p2)**3/special.gamma(1+3/p2)

    # superball surface radius for a point, a definition of radius in p2 but normal length unit
    r=lambda xyz:(np.abs(xyz[:,:3])**p2).sum(axis=1)**(1./p2)
    def _inside(xyz,R,dR=None):
        # points inside superball or in surface layer [R,R+dR]
        if dR is None:
            rr=r(xyz)
            inside= rr<=R
        else:
            rr=r(xyz)
            inside= (rr>R) & (rr<R+dR)
        return inside

    # surounding cubic grid as start
    D=R*3**0.5
    grid0=np.mgrid[-D:D:1j*nGrid,-D:D:1j*nGrid,-D:D:1j*nGrid].reshape(3,-1).T         # 89 µs
    # rotate to remove allignemnt of borders to grid
    rr=formel.rotationMatrix([1,1,1],alpha)
    grid=np.dot(grid0,rr)
    # grid with blength at last column
    gridb=np.c_[grid,np.ones(grid.shape[0])]                                    # 34 µsd=2*R/nGrid
    # distance gridpoints
    d=2.*D/(nGrid-1)
    volGridPoint=d**3
    insidegrid=[gridb[_inside(gridb,R-d/2.)]]
    surfgrid=gridb[_inside(gridb,R-d/2.,d)]
    # refine surfgrid
    # the cube for a gridpoint of edge length d is between [-d/2:d/2] , 8 new cubes at diagonals/4
    c8=np.mgrid[-1:1:1j*2, -1:1:1j*2,  -1:1:1j*2].reshape(3,-1).T/4.
    c8=np.dot(c8,rr)
    c8b=np.c_[c8,np.zeros(c8.shape[0])]
    while d>2*D/(nGrid-1)/3.:
        # new smaller cubes in the surfgrid
        #the centers of 8 cubes around point are point+c8b*d # add center point
        surfgrid=(surfgrid[:,None]+c8b*d).reshape(-1,4)
        surfgrid[:,3]/=8.  # reduce blength
        d=d/2.
        insidegrid.append(surfgrid[_inside(surfgrid,R-d/2.)])
        surfgrid=surfgrid[_inside(surfgrid,R-d/2.,d)]
    # a part of the surfgrid points has volume outside the surface
    # The volume of a gridpoint is d**3, the distance to the surface R-r(point)
    lastsurfgrid=surfgrid[_inside(surfgrid,R)]
    ##  some tries to improve which dont improve
    #dr=r(lastsurfgrid)  # distance to surface is R-r(point)
    #lastsurfgrid[:,3]*=(R-dr)/(2*d)  # reduce blength to include only the inside volume
    #lastsurfgrid[:,:3]=lastsurfgrid[:,:3]*R/dr[:,None] # move points to the surface
    insidegrid.append(lastsurfgrid)
    outsidegrid=insidegrid+[surfgrid[_inside(surfgrid,R,R+d/2.)]]
    insidegrid=np.vstack(insidegrid)
    outsidegrid=np.vstack(outsidegrid)
    # calc scattering
    #result=cloudScattering(q,insidegrid,nGrid=nGrid*4)
    result=cloudScattering(q,insidegrid,nFib=nGrid*4,V=volGridPoint)
    result.columnname='q; Iq; beta'
    result=result.addZeroColumns(2)
    result[-2]=result.Y
    resulto=cloudScattering(q,outsidegrid,nFib=nGrid,V=volGridPoint)
    result[-1]=resulto.Y
    result.Y=0.5*(result.Y*result.sumblength**2+resulto.Y*resulto.sumblength**2)/(0.5*(resulto.sumblength**2+result.sumblength**2))
    result.Y=result.Y*V**2*contrast**2
    # include for checking
    #result[-2]*=V**2*contrast**2
    #result[-1]*=V**2*contrast**2
    #result.columnname+='; Pin; Pout'
    result.modelname=sys._getframe().f_code.co_name
    result.R=R
    result.Volume=V
    result.rounding_p=p2/2.
    result.contrast=contrast
    result.I0=V**2*contrast**2
    if returngrid:
        result.grid=insidegrid
    return result


def _mVD(Q,kk,N):
    # in the paper N and n are both the same.
    q=Q#np.float128(Q) # less numeric noise at low Q with float128 but 4 times slower
    K=kk#np.float128(kk)
    K2=K*K
    K3=K2*K
    K4=K3*K
    K5=K4*K
    K6=K5*K
    K7=K6*K
    K8=K7*K
    NN=N*N
    NNN=N*N*N
    K2m1=K2-1
    K2p1=K2+1
    KN2=K**(N+2)
    D  =(-6.*K2m1*K2p1*(K4+5*K2+1)*NN+(-6*K8-12*K6+48*K4+48*K2+6)*N+(3*K8+36*K6+24*K4-18*K2-3.))  *np.sin(q*(2*N+1))
    D +=((3*K8-12*K6-45*K4-24*K2-3)*NN+(6*K8-12*K6-72*K4-48*K2-6)*N+(3*K8+18*K6-24*K4-36*K2-3.))  *np.sin(q*(2*N-1))
    D +=((3*K8+24*K6+45*K4+12*K2-3)*NN+6*K2*(3*K2+2)*N+3*K2*(4*K4-K2-6.))                         *np.sin(q*(2*N+3))
    D +=(18*K4*K2p1*NN+6*K2*(6*K4+3*K2-2)*N+3*K2*(6*K4+K2-4.))                                    *np.sin(q*(2*N-3))
    D +=(-18*K2*K2p1*NN-6*K4*(2*K2+3)*N-3*K4)                                                     *np.sin(q*(2*N+5))
    D +=(3*K4*NN+6*K4*N+3*K4)                                                                     *np.sin(q*(2*N-5))
    D +=(-3*K4*NN)                                                                                *np.sin(q*(2*N+7))
    D +=(6*K3*(3*K4+10*K2+5)*NN+6*K3*(3*K4+8*K2+3)*N-12*K*K2m1*(K4+3*K2+1.))                      *np.sin(q* 2*N   )
    D +=(K*(-12*K6-12*K4+12*K2+6)*NN-6*K*(2*K2+3)*(2*K4-2*K2-1)*N+K*(-12*K6-12*K4+36*K2+12.))     *np.sin(q*(2*N-2))
    D +=(K*(-30*K4-60*K2-18)*NN+K*(-42*K4-72*K2-18)*N+K*(-12*K6-36*K4+12*K2+12.))                 *np.sin(q*(2*N+2))
    D +=(-6*K3*(2*K2+1)*NN-6*K3*(4*K2+1.)*N-12*K5)                                                *np.sin(q*(2*N-4))
    D +=(-6*K*(K6+2*K4-2*K2-2)*NN+6*K3*(K4+4*K2+2.)*N+12*K3)                                      *np.sin(q*(2*N+4))
    D +=(6*K3*(K2+2.)*NN+6*K5*N)                                                                  *np.sin(q*(2*N+6))

    D +=(6*K2m1*K2p1*(K4+4*K2+1)*NNN+3*(K4-4*K2-3)*(3*K4+8*K2+1)*NN+(3*K8-36*K6-120*K4-60*K2-3)*N+42*K2*(K4-4*K2+1.))  \
                                                                                                         *np.sin(  q)
    D +=(-2*K2m1*K2p1*(K4-K2+1)*NNN+(-3*K8+9*K6+3*K2+3)*NN+(-K8+7*K6+5*K2+1)*N+6*K2*(-4*K4+11*K2-4.))    *np.sin(3*q)
    D +=(-6*K2*K2m1*K2p1*NNN-3*K2*(K4-8*K2-5)*NN+3*K2*(K4+8*K2+3)*N+6*K2*(K4-K2+1.))                     *np.sin(5*q)
    D +=(-6*K*K2m1*(2*K2+1)*(K2+2)*NNN+K*(-12*K6+48*K4+102*K2+24)*NN+K*(66*K4+84*K2+12)*N+24*K3*K2p1)    *np.sin(2*q)
    D +=(6*K*K2m1*K2p1*K2p1*NNN+6*K*K2p1*(K4-5*K2-2)*NN-6*K*K2p1*(5*K2+1)*N-12*K3*K2p1)                  *np.sin(4*q)
    D +=(2*K3*K2m1*NNN-6*K3*NN-2*K3*(K2+2.)*N)                                                           *np.sin(6*q)

    D +=KN2*K2m1*        np.sin(q* N+0 )*K*(-72-12*N*(3*K2+4))
    D +=KN2*K2m1*        np.sin(q*(N-1))*  ( 12*(3*K2-2)-12*N*(K2+2.))
    D +=KN2*K2m1*        np.sin(q*(N+1))*  (-12*(2*K2-3)+12*N*(4*K2+3.))
    D +=KN2*K2m1*        np.sin(q*(N-2))*K*(48+6*N*(4*K2+7.))
    D +=KN2*K2m1*        np.sin(q*(N+2))*K*(48+12*N*(2*K2+1.))
    D +=KN2*K2m1*        np.sin(q*(N-3))*  (-6*(4*K2-1)-6*N*(2*K2-1.))
    D +=KN2*K2m1*        np.sin(q*(N+3))*  (6*(K2-4)-6*N*(7*K2+4.))
    D +=KN2*K2m1*        np.sin(q*(N-4))*K*(-12-6*N*(K2+2.))
    D +=KN2*K2m1*        np.sin(q*(N+4))*K*(-12-6*N*(K2-2.))
    D +=KN2*K2m1*        np.sin(q*(N-5))*K2*(6.+6*N)
    D +=KN2*K2m1*        np.sin(q*(N+5))*  (6+6*N*(2*K2+1.))
    D +=KN2*K2m1*        np.sin(q*(N+6))*K*(-6.*N)

    return D # np.float64(D)

def _mVSzero(q,N):
    S=0.5+3./(4*N*(N+0.5)*(N+1))*(np.cos(2*q*(N+1))*          ( (N+1)**2-(N+1)/(  np.sin(q)**2)) +
                                  np.sin(2*q*(N+1))/np.tan(q)*(-(N+1)**2+    1/(2*np.sin(q)**2)))
    return S/N**2/q**2

def _mVSone(q,N):
    S=3./(N**3*(N+0.5)*(N+1)) * (-0.5 *np.cos(q*(N+0.5))*(N+0.5) +
                                  0.25*np.sin(q*(N+0.5))/np.tan(q/2.))**2
    return S/ (q*np.sin(q/2))**2

def _mVS(Q, R, displace, N):
    q=Q*R/N
    if N==1:
        # a single shell ; see Frielinghaus below equ. 5
        return np.sinc(Q*R/np.pi)**2
    if displace==0:
        return _mVSone(q,N)
    # for N > 1
    Sq  = np.ones_like(Q)
    K=_fa_sphere(Q * displace)

    # booleans to decide which solution
    limit=1e-3
    kzerolimit=limit * 0.5*(6*N**5+15*N**4+10*N**3-N)/(6.*N**5-10*N**3+4*N)
    konelimit =limit * (420. / 36 *  (4. * N ** 6 + 12 * N ** 5 + 13 * N ** 4 + 6 * N ** 3 + N ** 2) /
                     (10. * N ** 7 + 36. * N ** 6 + 21. * N ** 5 - 35 * N ** 4 - 35 * N ** 3 + 4 * N))
    kone=K > 1 - konelimit
    try:
        # above minimum Q with K <kzerolimit always use the kzero solution to get smooth solution
        Qmin=np.min(Q[K <kzerolimit])
    except ValueError:
        # This happens when kzerolimit is not in Q range and kzero should be always False
        Qmin=np.max(Q)+1
    kzero = Q > Qmin
    kk= ~(kzero | kone)
    # cases as described in Frielinghaus equ 12 and 13 and full solution (kk)
    S0=_mVSzero(q,N)
    Sq[kzero]=S0[kzero]
    Sq[kone]=_mVSone(q[kone],N)
    qkk=q[kk]
    D = _mVD( qkk, K[kk],N)
    divisor=(-48.*np.sin(qkk)**3 * (K[kk]**2 + 1 - 2*K[kk] * np.cos(qkk))**4 * qkk**2)
    sq=      D *   3. / (N**3*(N+0.5)*(N+1)) / divisor
    # for some values divisor and D become both small (machine precision) introducing errors
    # these are approximated by _mVSzero which has minima at the same positions
    qsing=(np.abs(D)< 1e-7) & (np.abs(divisor)< 1e-7) & (S0[kk]<1e-4)
    sq[qsing ]=_mVSzero(qkk[qsing],N)

    Sq[kk] = sq
    return Sq  #,_mVD( q, K,N),(-48.*np.sin(q)**3 * (K**2 + 1 - 2*K * np.cos(q))**4 * q**2),_mVSone(q,N)

def _mVFq(Q, shelld,sld,ds=0):
    # form factor of a symmetric multilayer with increasing thickness shelld
    shd = np.cumsum(np.r_[shelld[0]/2.,shelld[1:]])*2.
    sld=sld.copy()
    # change innermost layer thickness, but cut at 0.1
    shd = shd + ds #max(shd[0] + ds, shd[0] * 0.1)
    if shd[0] > 0:
        if sld.shape[0]>1:
            sld[:-1]=sld[:-1]-sld[1:] # differences in scattering length densities
        Aq = np.sum(sld[:,None]*np.sinc(Q * shd[:,None] / 2./np.pi),axis=0)
    else:
        Aq=np.ones_like(Q)
    ret= dA(np.c_[Q, Aq**2 ].T)
    return ret

def _discrete_gaussian_kernel(mean,sig,Nmax):
    # generates a truncated discrete gaussian distribution with integrated probabilities in the intervalls
    if sig<0.4:
        # some default values for a single shell
        return [mean],[1],mean,0
    if Nmax==0:
        b=10  # 10 sigma is large enough and >5*sig
    else:
        b=(Nmax-mean)/sig
    nn=np.floor(np.r_[mean-5*sig:mean+5*sig])
    nn=nn[nn>0]
    cdf=scipy.stats.truncnorm.cdf(np.r_[nn-0.5,nn[-1]+0.5],a=(0.5-mean)/sig,b=b,loc=mean,scale=sig)
    m,v= scipy.stats.truncnorm.stats(a=(0.5 - mean) / sig, b=10, loc=mean, scale=sig ,moments='mv')
    pdf = np.diff(cdf)
    take=pdf>0.005
    return nn[take],pdf[take]/np.sum(pdf[take]),m,v**0.5

def multilamellarVesicles(Q, R, N, phi, displace=0, dR=0, dN=0,shellthickness=0,ds=0, SLD=1, solventSLD=0,nGauss=100):
    r"""
    Scattering intensity of a multilamellar vesicle with random displacement of the inner vesicles [1]_.

    The result contains the full scattering, the structure factor of the shells and a multilayer formfactor of the
    lamellar layer structure. Other layer structures as mentioned in [2]

    Parameters
    ----------
    Q : float
        Wavevector in 1/nm.
    R : float
        Outer radius of the Vesicle in units nm.
    dR : float
        Width of outer radius distribution in units nm.
    displace : float
        Displacements of the vesicles centers in units nm.
        This describes the displacement steps in a random walk of the centers.
        displace=0 it is concentric, all have same center. displace< R/N.
    N : int
        Number of layers.
    dN : int, default=0
        Width of distribution for number of layers. (dN< 0.4 is single N)
        A zero truncated normal distribution is used with N>0 and N<R/displace.
        Check .Ndistribution and .Nweight = Nweigth for the used distribtion.
    shellthickness: float,list of float,default=0
        Thickness of shells in symetric layer in units nm.
        Zero assumes infinit thin layer with constant formfactor.
        List gives consecutive layer thickness from center to outside.
        [4,1] result in a [1,4,1] symmetric layer.
    ds : float, not working , set to zero
        Thickness fluctuation of the innermost layer in shellthickness. unit is nm.
        A Gaussian is used which is cut at 0.1*shellthickness[0].
        ds should be significant smaller than shellthickness[0].
    phi : float
        Volume fraction :math:`\phi` of layers inside of vesicle.
    SLD : float
        Scattering length density of shells in nm^-2.
    solventSLD
        Solvent scattering length density in nm^-2.

    Returns
    -------
        dataArray with [q,I(q),S(q),F(q)]
         .columnname='q;Iq;Sq;Fq'
         .outerShellVolume
         .Ndistribution
         .Nweight
         .displace
         .phi
         .shellthickness
         .SLD
         .solventSLD
         .shellfluctuations=ds
         .preFactor=phi*Voutershell**2


    Notes
    -----
    The left shows a concentric lamellar structure.
    The right shows the random path of the consecutive centers of the spheres.
    See :ref:`Multilamellar Vesicles` for resulting scattering curves.

    .. image:: MultiLamellarVesicles.png
     :align: center
     :height: 200px
     :alt: Image of MultiLamellarVesicles


    The function returns I(Q) as (see [1]_ equ. 17 )

    .. math:: I(Q)=\phi V_{outershell} S(Q) F(Q)

    .. math:: F(Q)= ( \sum_i d \rho_i sinc( Q d_i) )^2

    with :math:`d\rho` as scattering length density difference to next layer
    with thickness :math:`d_i` and
    the shell structure factor :math:`S(Q)` as described in equ. A2 in [1]_.

    - The amphiphile concentration phi
      is roughly given by phi = d/a, with d being the bilayer thickness
      and a being the spacing of the shells. The spacing of the
      shells is given by the scattering vector of the first correlation
      peak, i.e., a = 2pi/Q. Once the MLVs leave considerable
      space between each other then phi < d/a holds. This condition
      coincides with the assumption of dilution of the Guinier law. (from [1]_)
    - Structure factor part is normalized that :math:`S(0)=\sum_{j=1}^N (j/N)^2`
    - To use a different shell form factor the structure factor is given explicitly.
    - Comparing a unilamellar vesicle (N=1) with multiShellSphere shows that
      R is located in the center of the shell::

        Q=js.loglist(0.0001,5,1000)#np.r_[0.01:5:0.01]
        ffmV=js.ff.multilamellarVesicles
        p=js.grace()
        # comparison double sphere
        mV=ffmV(Q=Q, R=100., displace=0, dR=0,N=1,dN=0, phi=1,shellthickness=6, SLD=1e-4,nGauss=20)
        p.plot(mV)
        p.plot(js.ff.multiShellSphere(Q,[97,6],[0,1e-4]),li=1)
        p.yaxis(label='S(Q)',scale='l',min=1e-10,max=1e6,ticklabel=['power',0])
        p.xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])

    Examples
    --------
    See :ref:`Multilamellar Vesicles`
    ::

     import jscatter as js
     import numpy as np

     ffmV=js.ff.multilamellarVesicles
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
     #
     p.legend(x=0.015,y=1e-1)
     p.subtitle('R=50 nm, N=5, shellthickness=[1.5,3.5,1.5] nm, dR=5, ds=0.')
     p.yaxis(label='S(Q)',scale='l',min=1e-6,max=1e4,ticklabel=['power',0])
     p.xaxis(label='Q / nm\S-1',scale='l',min=1e-2,max=5,ticklabel=['power',0])


    References
    ----------
    .. [1] Small-angle scattering model for multilamellar vesicles
           H. Frielinghaus PHYSICAL REVIEW E 76, 051603 (2007)
    .. [2] Small-Angle Scattering from Homogenous and Heterogeneous Lipid Bilayers
           NorbertKučerka Advances in Planar Lipid Bilayers and Liposomes 12, 201-235 (2010)
    """
    if isinstance(shellthickness,(float,int)): shellthickness=[shellthickness]

    # formfactor
    shelld = np.atleast_1d(shellthickness)
    sld=np.atleast_1d(SLD)-solventSLD
    if ds>0 and shelld[0] > 0 :
        # integrate over normal distribution with width ds
        x,w=formel.gauss(np.r_[-3*ds:3*ds:37j],0,ds).array
        fq=dL([_mVFq(Q=Q, shelld=shelld,sld=sld,ds=xx) for xx,ww in zip(x,w)])
        Fq=(fq.Y.array*w[:,None]).sum(axis=0)/w.sum()
    else:
        # no thickness fluctution
        Fq = _mVFq(Q, shelld, sld).Y

    if shelld[0]==0 or phi==0:
        # if shellthickness is zero
        Voutershell=1
        phi=1
    else:
        shellmax=np.cumsum(np.r_[shellthickness[0]/2.,shellthickness[1:]])[-1]*2.
        Voutershell = 4 * np.pi * R ** 2 * shellmax  # last shelld is max thickness of shell
    if N*(displace+np.max(shelld))>R:
        warnings.warn("--->>  Warning: layers dont fit inside!!!  N*(displace+np.max(shelld)) > R")

    # get discrete distribution over N with width dN
    # for small dN this is a single N and N>0
    Nmax=R/displace if displace!=0 else 0
    Ndistrib,Nweigth,Nmean,Nsigma=_discrete_gaussian_kernel(N,dN,Nmax)

    # define sum over N distribution
    SqR=lambda RR:np.c_[[Nw*_mVS(Q, RR, displace, NN) for NN,Nw in zip(Ndistrib,Nweigth)]].sum(axis=0)

    # integrate over dR
    Sq=np.c_[[Nw*_mVS(Q, R, displace, NN) for NN,Nw in zip(Ndistrib,Nweigth)]].sum(axis=0)
    if dR==0:
        Sq=np.c_[[Nw*_mVS(Q, R, displace, NN) for NN,Nw in zip(Ndistrib,Nweigth)]].sum(axis=0)
    else:
        # fixed Gaussian integral over +-dR
        weight=formel.gauss(np.r_[R-3*dR:R+3*dR:17j],R,dR).array
        Sq=formel.pQFG(SqR, R-3*dR, R+3*dR, 'RR', n=nGauss, weights=weight)

    result=dA(np.c_[Q,phi*Voutershell**2*Fq*Sq,Sq,Fq].T)
    #result = dA(np.c_[Q, Sq].T)
    result.modelname=sys._getframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname='q;Iq;Sq;Fq'
    result.outerShellVolume=Voutershell
    result.Ndistribution=Ndistrib
    result.Nweight = Nweigth
    result.displace=displace
    result.phi=phi
    result.shellthickness=shellthickness
    result.SLD=SLD
    result.solventSLD = solventSLD
    result.shellfluctuations=ds
    result.preFactor=phi*Voutershell**2
    return result
