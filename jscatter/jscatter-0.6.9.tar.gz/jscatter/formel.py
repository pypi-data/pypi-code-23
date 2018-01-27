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
Physical equations and useful formulas as quadrature of vector functions,
viscosity, compressibility of water, scatteringLengthDensityCalc or sedimentationProfile.
Use scipy.constants for physical constants.

- Each topic is not enough for a single module, so this is a collection.
- Return values are dataArrays were useful. To get only Y values use .Y
- All scipy functions can be used. See http://docs.scipy.org/doc/scipy/reference/special.html.
- Statistical functions http://docs.scipy.org/doc/scipy/reference/stats.html.

Mass and scattering length of all elements in Elements are taken from :
 - Mass: http://www.chem.qmul.ac.uk/iupac/AtWt/
 - Neutron scattering length: http://www.ncnr.nist.gov/resources/n-lengths/list.html
Units converted to amu for mass and nm for scattering length.

"""
from __future__ import division
from __future__ import print_function

import functools
import inspect
import math
import numpy as np
import os
import re
import scipy
import scipy.constants as constants
import scipy.integrate
import scipy.special as special
import sys
import warnings
from collections import deque
from scipy import stats
from scipy.special.orthogonal import p_roots
import pickle
import io

from . import parallel
from .dataarray import dataArray as dA
from .dataarray import dataList as dL

_path_=os.path.realpath(os.path.dirname(__file__))

#: variable to allow printout for debugging as if debug:print 'message'
debug=False

# load table with neutron scattering cross sections
with io.open(_path_+'/Neutronscatteringlengthsandcrosssections.html') as _f:
    Nscatdat=_f.readlines()

#: dictionary with coherent and incoherent neutron scattering length
#: units nm
Nscatlength={}

Hnames={'1H':'h','2H':'d','3H':'t'}
for line in Nscatdat[115+3:486+3]:
    words=[w.strip() for w in line.split('<td>')]
    if words[1] in Hnames.keys():
        Nscatlength[Hnames[words[1]]]=[float(words[3])*1e-6,np.sqrt(float(words[6])/4/np.pi*1e-10)]
    elif words[1][0] not in '0123456789':
        try:
            Nscatlength[words[1].lower()]=[float(words[3])*1e-6,np.sqrt(float(words[6])/4/np.pi*1e-10)]
        except:
            try:
                Nscatlength[words[1].lower()]=[complex(words[3])*1e-6,np.sqrt(float(words[6])/4/np.pi*1e-10)]
            except:
                Nscatlength[words[1].lower()]=[-0,-0]

#  [Z,mass,b_coherent,b_incoherent,name]
#: Elements Dictionary
#: with: { symbol : (electron number; mass; neutron coherent scattering length, neutron incoherent scattering length, name) };
#: units amu for mass and nm for scattering length
Elements={}
# load periodic table perhaps later more of this
with io.open(_path_+'/elementsTable.dat') as _f:
    for ele in _f.readlines():
        if ele[0]=='#': continue
        z,symbol,name,mass=ele.split()[0:4]
        try:
            Elements[symbol.lower()]=(int(z),
                                      float(mass),
                                      Nscatlength[symbol.lower()][0],
                                      Nscatlength[symbol.lower()][1],
                                      name)
        except:
            pass

# load table with density parameters accordiing to
# Densities of binary aqueous solutions of 306 inorganic substances
# P. Novotny, O. Sohnel J. Chem. Eng. Data, 1988, 33 (1), pp 49–55 DOI: 10.1021/je00051a018
_aquasolventdensity={}
with open(_path_+'/aqueousSolutionDensitiesInorganicSubstances.txt') as _f:
    for ele in _f.readlines():
        if ele[0]=='#': continue
        # substance A*10^-2 -B*10 C*10^3 -D E*10^2 -F*10^4 st*10^2 t Cmax-
        aname,A,B,C,D,E,F,s,Trange,concrange=ele.split()[0:10]
        try:
            _aquasolventdensity[aname.lower()]=(float(A)*1e2,
                                                -float(B)*1e-1,
                                                float(C)*1e-3,
                                                -float(D)*1e0,
                                                float(E)*1e-2,
                                                -float(F)*1e-4,
                                                float(s)/100.,
                                                Trange,
                                                concrange)
        except:
            pass
_aquasolventdensity['c4h11n1o3']=(0.0315602,0.708699)   #: TRIS buffer density    DOI: 10.1021/je900260g
_aquasolventdensity['c8h19n1o6s1']=(0.0774654,0.661610) #: TABS buffer density    DOI: 10.1021/je900260g

_bufferDensityViscosity={}
with io.open(_path_+'/bufferComponents.txt','r') as _f:
    for ele in _f.readlines():
        if ele[0]=='#': continue
        # substance
        name,dc0,dc1,dc2,dc3,dc4,dc5,vc0,vc1,vc2,vc3,vc4,vc5,unit,crange=ele.split()
        temp=[float(ss) for ss in [dc0,dc1,dc2,dc3,dc4,dc5,vc0,vc1,vc2,vc3,vc4,vc5] ]
        _bufferDensityViscosity[name.lower()]=tuple(temp)+(unit, crange)
        #except:
        #    pass
    del ele

felectron=2.8179403267e-6   #: Cross section of electron in nm
kB=0.00831447086363271      #: Boltzmann constant in kJ/(mol⋅K)

def _getFuncCode(func):
    """
    Get code object of a function
    Should work  for python 2&3
    """
    try:
        return func.func_code  # python2
    except:
        return func.__code__  # python3


def memoize(**memkwargs):
    """
    A least-recently-used cache decorator to cache expensive function evaluations.

    Function results are cached with specified memkwargs replaced by a list of values that are repeatedly evaluated.
    This is useful if it is cheap to evaluate the function for an argument as list compared to evaluation of single values.
    Assume we fit a series of measurements with fixed Q1,..Qm and changing fit parameters p1..pn.
    Instead of calculating F(Q,a,b)=Q*Bnm(a,b) each time we calc F for the list of all Q at once and get the F(Qi,p1..pn)
    from the cache or interpolate.

    Parameters
    ----------
    function : function
        Function to evaluate as e.g. f(Q,a,b,c,d)
    memkwargs : dict
        Keyword args and values to cache. May be empty  for normal caching of a function.
         {'Q':np.r_[0:10:0.1],'t':np.r_[0:100:5]}
    maxsize : int, default 128
        maximum size of the cache. Last is dropped.

    Returns
    -------
        cached function with new methods
         - last(i) to retrieve the ith evaluation result in cache (last is i=-1).
         - clear() to clear the cached results.
         - hitsmisses counts hits and misses.

    Notes
    -----
    Only keyword arguments for the memoized function are supported!!!!
    Only one attribute and X are supported for fitting as .interpolate works only for two cached attributes.


    Examples
    --------
    Use it like this::

     import jscatter as js
     import numpy as np

     # define some data
     TT=js.loglist(0.01,80,30)
     QQ=np.r_[0.1:1.5:0.15]
     # in the data we have 'q' and 'X'
     data=js.dynamic.finiteZimm(t=TT,q=QQ,NN=124,pmax=100,tintern=10,ll=0.38,Dcm=0.01,mu=0.5,viscosity=1.001,Temp=300)

     # a short definition for the same as below
     # makes a unique list of all X values    -> interpolation is exact for X
     tt=list(set(data.X.flatten));tt.sort()
     # use correct values from data for q     -> interpolation is exact for q
     fZ=js.formel.memoize(q=data.q,t=tt)(js.dynamic.finiteZimm)
     def fitfunc(Q,Ti,NN,tint,ll,D,mu,viscosity,Temp):
        res= fZ(t=Ti,q=Q,NN=NN,tintern=tint,ll=ll,Dcm=D,pmax=40,mu=mu,viscosity=viscosity,Temp=Temp)
        return res.interpolate(q=Q,X=Ti,deg=2)[0]

     # do the fit
     data.setlimit(tint=[0.5,40],D=[0,1])
     data.makeErrPlot(yscale='l')
     NN=20
     data.fit(fitfunc,{'tint':10,'D':0.1,},{'NN':20,'ll':0.38/(NN/124.)**0.5,'mu':0.5,'viscosity':0.001,'Temp':300},mapNames={'Ti':'X','Q':'q'},)

     # define the function to memoize, first the long usual way as decorator
     @js.formel.memoize(Q=np.r_[0:3:0.2],Time=np.r_[0:50:0.5,50:100:5])
     def fZ(Q,Time,NN,tintern,ll,Dcm,mu,viscosity,Temp):
         # finiteZimm accepts t and q as array and returns a dataList with different Q and same X=t
         res=js.dynamic.finiteZimm(t=Time,q=Q,NN=NN,pmax=20,tintern=tintern,ll=ll,Dcm=Dcm,mu=mu,viscosity=viscosity,Temp=Temp)
         return res
     # define the fitfunc
     def fitfunc(Q,Ti,NN,tint,ll,D,mu,viscosity,Temp):
        res= fZ(Time=Ti,Q=Q,NN=NN,tintern=tint,ll=ll,Dcm=D,mu=mu,viscosity=viscosity,Temp=Temp) #this is the cached result for the list of Q
        # interpolate for the single Q value the cached result has again 'q'
        return res.interpolate(q=Q,X=Ti,deg=2)[0]
     # do the fit
     data.setlimit(tint=[0.5,40],D=[0,1])
     data.makeErrPlot(yscale='l')
     data.fit(fitfunc,{'tint':6,'D':0.1,},{'NN':20,'ll':0.38/(20/124.)**0.5,'mu':0.5,'viscosity':0.001,'Temp':300},mapNames={'Ti':'X','Q':'q'})
     # the result depends on the interpolation;


    """
    if 'maxsize' in memkwargs:
        cachesize =memkwargs['maxsize']
        del memkwargs['maxsize']
    else:
        cachesize=128
    def _memoize(function):
        function.hitsmisses=[0,0]
        cache = function.cache = {}
        deck  = function.deck = deque([], maxlen = cachesize)
        function.last = lambda i=-1:function.cache[function.deck[i]]
        def clear():
            while len(function.deck)>0:
                del function.cache[function.deck.pop()]
            function.hitsmisses=[0,0]

        function.clear=clear
        @functools.wraps(function)
        def _memoizer(*args, **kwargs):
            # make new
            key=pickle.dumps(args, 1)+pickle.dumps(kwargs, 1)
            if key in cache:
                function.hitsmisses[0]+=1
                deck.remove(key)
                deck.append(key)
                return cache[key]
            else:
                function.hitsmisses[1]+=1
                cache[key] = function(*args, **dict(kwargs,**memkwargs))
                if len(deck)>=cachesize:
                    del cache[deck.popleft()]
                deck.append(key)
                return cache[key]
        return _memoizer
    return _memoize

#: fibonacciLatticePointsOnSphere; see :func:`parallel.fibonacciLatticePointsOnSphere`
fibonacciLatticePointsOnSphere=parallel.fibonacciLatticePointsOnSphere

def loglist(mini=0.1,maxi=5,number=100):
    """
    Log like distribution between mini and maxi with number points.

    Parameters
    ----------
    mini,maxi : float, default 0.1, 5
        start, endpoint
    number : int, default 100
        number of points

    Returns
    -------
        ndarray

    """
    return np.exp(
        np.r_[np.log((mini if mini!=0. else 1e-6)):np.log((maxi if maxi!=0 else 1.)):(number if number!=0 else 10)*1j])

def smooth(data, windowlen=6, window='flat'):
    """
    Smooth data using a window with requested size and type.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal (with the window size)
    in both ends so that transient parts are minimized in the begining and end part of the output signal.
    Adapted from SciPy/Cookbook.

    Parameters
    ----------
    data : array
        Data to smooth
    windowlen : int, default = 6
        The length of the smoothing window; should be an odd integer (is forced to next larger odd int).
        Smaller 3 returns unchanged data.
    window :  'hanning', 'hamming', 'bartlett', 'blackman', default ='flat'
        Type of window.
        'flat' will produce a moving average smoothing.

    Return
    ------
        array (the smoothed signal)

    Examples
    --------

    t=linspace(-2,2,0.1)
    data=sin(t)+randn(len(t))*0.1
    y=smooth(data)

    Notes
    -----
    See  numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve

    """
    windowlen=int(np.ceil(windowlen/2)*2)

    if hasattr(data,'_isdataArray'):
        data=data.Y
    if data.size < windowlen:
        raise ValueError("Input vector needs to be bigger than window size.")
    if windowlen<3:
        return data

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s=np.r_[data[windowlen - 1:0:-1], data, data[-1:-windowlen:-1]]
    if window == 'flat': #moving average
        w=np.ones(windowlen, 'd')
    else:
        w=eval('np.'+window+'(windowlen)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    res=y[int((windowlen / 2 - 1)):int(-(windowlen / 2))]
    return res


def rotationMatrix(vector,angle):
    """
    Create a rotation matrix corresponding to rotation around vector v by a specified angle.

    .. math::  R = vv^T + cos(a) (I - vv^T) + sin(a) skew(v)

    Parameters
    ----------
    vector : array
        Rotation around a general  vector
    angle : float
        Angle in rad

    Returns
    -------
        Rotation matrix

    Examples
    --------
    ::

     R=js.formel.rotationMatrix([0,0,1],np.deg2rad(-90))
     v=[1,0,0]
     rv=np.dot(R,v)
     #
     # rotate fibonacci Grid
     qfib=js.formel.fibonacciLatticePointsOnSphere(300,1)
     qfib=qfib[qfib[:,2]<np.pi/2,:]           # select half sphere
     qfib[:,2]*=(30/90.)                      # shrink to cone of 30°
     qfx=js.formel.rphitheta2xyz(qfib)        # transform to cartesian
     R=js.formel.rotationMatrix([0,1,0],np.deg2rad(-90)) # rotation around y axis
     Rfx=np.einsum('ij,jk->ki',R,qfx.T)                  # do rotation
     fig = pyplot.figure()
     ax = fig.add_subplot(111, projection='3d')
     sc=ax.scatter(qfx[:,0], qfx[:,1], qfx[:,2], s=2, color='r')
     sc=ax.scatter(Rfx[:,0], Rfx[:,1], Rfx[:,2], s=2, color='b')
     ax.scatter(0,0,0, s=55, color='g',alpha=0.5)
     pyplot.show(block=False)

    """
    d=np.array(vector,dtype=np.float64)
    d/=np.linalg.norm(d)
    eye=np.eye(3,dtype=np.float64)
    ddt=np.outer(d,d)
    skew=np.array([[0,d[2],-d[1]],
                   [-d[2],0,d[0]],
                   [d[1],-d[0],0]],dtype=np.float64)
    mtx=ddt+np.cos(angle)*(eye-ddt)+np.sin(angle)*skew
    return mtx

def box(x,edges=[0],edgevalue=0, rtol=1e-05, atol=1e-08):
    """
    Box function with smoothed edges.

    For equal edges and edgevalue> 0 the delata function is given.


    Parameters
    ----------
    x : array
    edges :  list of float, float
        Edges of the box.
        If only one number is given  the box goes from [-edge:edge]
    edgevalue : float, default=0
        Value to use if x==edge for both edges.
    rtol,atol : float
        The relative/absolute tolerance parameter for the edge detection.
        See numpy.isclose.

    Returns
    -------
        dataArray

    Notes
    -----
    Edges may be smoothed by convolution with a Gaussian.::

     edge=2
     x=np.r_[-4*edge:4*edge:200j]
     f=js.formel.box(x,edges=edge)
     res=js.formel.convolve(f,js.formel.gauss(x,0,0.2))


    """
    edges=np.atleast_1d(edges)
    if edges.shape[0]<2:edges=np.r_[-abs(edges[0]),abs(edges[0])]

    v=np.zeros_like(x)
    v[(x>edges[0]) & (x<edges[1])]=1
    v[(np.isclose(x,edges[0])) | (np.isclose(x,edges[1]))]=edgevalue
    box=dA(np.c_[x,v].T)
    box.setColumnIndex(iey=None)
    box.modelname=sys._getframe().f_code.co_name
    return box

def gauss(x,mean=1,sigma=1):
    """
    Normalized Gaussian function.

    g(x)=exp(-0.5*(x-mean)**2/sigma**2)/sigma/np.sqrt(2*np.pi)
    
    Parameters
    ----------
    x : float
        array of x values
    mean : float
        mean value
    sigma : float
        1/e width

    Returns
    -------
    dataArray

    """
    x=np.atleast_1d(x)
    result=dA(np.c_[x,np.exp(-0.5*(x-mean)**2/sigma**2)/sigma/np.sqrt(2*np.pi)].T)
    result.setColumnIndex(iey=None)
    result.mean=mean
    result.sigma=sigma
    result.modelname=sys._getframe().f_code.co_name
    return result

def lorentz(x,mean=1,gamma=1):
    """
    Normalized Lorentz function

    f(x) = gamma/((x-mean)**2+gamma**2)/np.pi
    
    Parameters
    ----------
    gamma : float
        half width half maximum 
    mean : float
        mean value
    
    Returns
    -------
    dataArray
    """
    x=np.atleast_1d(x)
    result=dA(np.c_[x,gamma/((x-mean)**2+gamma**2)/np.pi].T)
    result.setColumnIndex(iey=None)
    result.mean=mean
    result.gamma=gamma
    result.modelname=sys._getframe().f_code.co_name
    return result

def lognorm(x,mean=1,sigma=1):
    """
    Lognorml distribution function

    Parameters
    ----------
    x : array
        x values
    mean : float
        mean
    sigma : float
        sigma

    Returns
    -------
        dataArray

    """
    mu=math.log(mean**2/(sigma+mean**2)**0.5)
    nu=(math.log(sigma/mean**2+1))**0.5
    distrib=stats.lognorm(s=nu,scale=math.exp(mu))
    result=dA(np.c_[x,distrib.pdf(x)].T)
    result.setColumnIndex(iey=None)
    result.mean=mean
    result.sigma=sigma
    result.modelname=sys._getframe().f_code.co_name
    return result

def voigt(x, center=0, fwhm=1,lg=1,asym=0, amplitude=1):
    """
    Voigt function for peak analysis.

    The Voigt function is a convolution of gaussian and lorenzian shape peaks for peak analysis.
    The lorenzian shows a stronger contribution outside FWHM with a sharper peak.
    Asymmetry of the shape can be added by a sigmoidal change of the FWHM [2]_.

    Parameters
    ----------
    x : array
        axis values
    center : float
        center of the distribution
    fwhm : float
        full width half maximum of the Voigt function
    lg : float, default = 1
        | lorenzian/gaussian fraction of both FWHM, describes the contributions of gaussian and lorenzian shape.
        | lorenzian/gaussian >> 1  lorenzian,
        | lorenzian/gaussian ~  1  central part gaussian, outside lorenzian wings
        | lorenzian/gaussian << 1. gaussian
    asym : float, default=0
        asymmetry factor in sigmoidal as :math:`2*fwhm/(1+np.exp(asym*(x-center)))`
        For a=0 the Voigt is symmetric with fwhm.
    amplitude : float, default = 1
        amplitude

    Returns
    -------
    dataArray


    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Voigt_profile
    .. [2] Aaron L. Stancik, Eric B. Brauns
           A simple asymmetric lineshape for fitting infrared absorption spectra
           Vibrational Spectroscopy 47 (2008) 66–69


    """
    ln2=math.log(2)
    # calc the fwhm in gauss and lorenz to get the final FWHM in the Voigt function with an accuracy of 0.02%
    # as given in Olivero, J. J.; R. L. Longbothum (February 1977).
    # Empirical fits to the Voigt line width: A brief review". Journal of Quantitative Spectroscopy and Radiative Transfer. 17 (2): 233–236.
    # doi:10.1016/0022-4073(77)90161-3
    FWHM=fwhm/(0.5346*lg+(0.2166*lg**2+1)**0.5)

    z =lambda fwhm: ( (x-center)+ 1j* lg * fwhm/2. )/math.sqrt(2) / (fwhm/(2*np.sqrt(2*ln2)))
    # the sigmoidal fwhm for asymmetry
    afwhm=lambda fwhm,a: 2*fwhm/(1+np.exp(a*(x-center)))
    # calc values with asymmetric FWHM
    val = amplitude / (afwhm(FWHM,asym)/ (2*np.sqrt(2*ln2))) / math.sqrt(2*np.pi) * special.wofz(z(afwhm(FWHM,asym))).real

    sigma=(FWHM/ (2*np.sqrt(2*ln2)))
    gamma=FWHM/2.
    result=dA(np.c_[x,val].T)
    result.setColumnIndex(iey=None)
    result.center=center
    result.sigma=sigma
    result.gamma=gamma
    result.fwhm=fwhm
    result.asymmetry=asym
    result.lorenzianOverGaussian=lg
    result.modelname=sys._getframe().f_code.co_name
    return result

def Ea(x,a,NN=100):
    """
    Mittag-Leffler function for real x>0 and 0<a<1

    .. math:: E(x,a)=\sum_{k=0}^{\inf} \\frac{x^k}{\Gamma(1+ak)}

    Parameters
    ----------
    x : array
        values
    a : float
        power
    NN : int, fefault=100
        limit for k


    References
    ----------

    """
    res= sum([x**k/scipy.special.gamma(a*k+1) for k in range(NN)])
    return res

########################################################################
# quadrature

class AccuracyWarning(Warning):
    pass

def _cached_p_roots(n):
    """
    Cache p_roots results to speed up calls of the fixed_quad function.
    """
    #scipy.integrate.quadrature
    if n in _cached_p_roots.cache:
        return _cached_p_roots.cache[n]

    _cached_p_roots.cache[n] = p_roots(n)
    return _cached_p_roots.cache[n]
_cached_p_roots.cache = dict()

def parQuadratureFixedGauss(func, lowlimit, uplimit, parname, n=5, weights=None, **kwargs):
    """
    Compute a definite integral using fixed-order Gaussian quadrature .

    Integrate func over parname from a to b using Gauss-Legendre quadrature [1]_ of order `n` for all .X.
    If function returns ndarray all is integrated and returned as ndarray.
    If function returns dataArray, only the .Y values is integrated and returned as dataArray.

    Parameters
    ----------
    func : callable
        A Python function or method  returning a vector array of dimension 1.
        If func returns dataArray .Y is integrated.
    lowlimit : float
        Lower limit of integration.
    uplimit : float
        Upper limit of integration.
    parname : string
        Name of the integration variable which should be a scalar.
        after evaluation the correspinding attribute ahs the mean value with weights.
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname e.g. a Gaussian with a<weights[0]<b and weights[1] contains weight values
        - Missing values are linear interpolated (faster). If None equal weights are used.
    kwargs : dict, optional
        Extra keyword arguments to pass to function, if any.
    n : int, optional
        Order of quadrature integration. Default is 5.

    Returns
    -------
    val : array, dataArray
        Gaussian quadrature approximation to the integral


    Examples
    --------
    ::

     t=np.r_[1:100]
     gg=js.formel.gauss(t,50,10)
     js.formel.parQuadratureFixedGauss(js.formel.gauss,0,100,'x',mean=50,sigma=10,n=50)

    Notes
    -----
    Reimplementation of scipy.integrate.quadrature.fixed_quad to work with vector output of the integrand function and weights .

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Gaussian_quadrature

    """
    x, w = _cached_p_roots(n)
    x = np.real(x)
    if np.isinf(lowlimit) or np.isinf(uplimit):
        raise ValueError("Gaussian quadrature is only available for finite limits.")
    y = (uplimit - lowlimit) * (x + 1) / 2.0 + lowlimit
    if weights is not None:
        wy=np.interp(y,weights[0],weights[1])
        normfactor=np.trapz(weights[1],weights[0])
        parmean=np.trapz(weights[1]*weights[0],weights[0])/normfactor
    else:
        wy=np.ones_like(y)
        normfactor= uplimit - lowlimit
        parmean= (uplimit + lowlimit) / 2
    res=[func(**dict(kwargs,**{parname:yy})) for yy in y]
    if isinstance(res[0],dA):
        Y=[r.Y for r in res]
        res[0].Y= (uplimit - lowlimit) / 2.0 * np.sum(w * wy * np.atleast_2d(Y).T, axis=-1)
        res[0].weightNormFactor=normfactor
        setattr(res[0],parname,parmean)
        return res[0]
    else:
        return (uplimit - lowlimit) / 2.0 * np.sum(w * wy * np.atleast_2d(res).T, axis=-1)

pQFG=parQuadratureFixedGauss

def parQuadratureAdaptiveGauss(func, lowlimit, uplimit, parname, weights=None, tol=1.e-8, rtol=1.e-8, maxiter=50, miniter=8, **kwargs):
    """
    Compute a definite integral using fixed-tolerance Gaussian quadrature for vector output.

    Adaptive integration of func from `a` to `b` using Gaussian quadrature adaptivly increasing number of points by 8.
    If function returns ndarray each element is integrated and returned as ndarray of same dimension.
    If function returns dataArray, only the .Y values is integrated and returned as dataArray.

    Parameters
    ----------
    func : function
        A Python function or method to integrate.
    lowlimit : float
        Lower limit of integration.
    uplimit : float
        Upper limit of integration.
    parname : string
        name of the integration variable which should be a scalar.
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname e.g. a Gaussian with a<weights[0]<b and weights[1] contains weight values
        - Missing values are linear interpolated (faster). If None equal weights are used.
    kwargs : dict, optional
        Extra keyword arguments to pass to function, if any.
    tol, rtol : float, optional
        Iteration stops when error between last two iterates is less than
        `tol` OR the relative change is less than `rtol`.
    maxiter : int, default 50, optional
        Maximum order of Gaussian quadrature.
    miniter : int, default 8, optional
        Minimum order of Gaussian quadrature.

    Returns
    -------
    val : float
        Gaussian quadrature approximation (within tolerance) to integral for all vector elements.
    err : float
        Difference between last two estimates of the integral.

    Examples
    --------
    ::

     t=np.r_[1:100]
     gg=js.formel.gauss(t,50,10)
     js.formel.parQuadratureAdaptiveGauss(js.formel.gauss,0,100,'x',mean=50,sigma=10)

    Notes
    -----
    Reimplementation of scipy.integrate.quadrature.quadrature to work with vector output of the integrand function.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Gaussian_quadrature


    """
    val = np.inf
    err = np.inf
    maxiter = max(miniter+1, maxiter)
    for n in range(maxiter ,miniter, -8)[::-1]:
        result = parQuadratureFixedGauss(func, lowlimit, uplimit, parname, n,weights, **kwargs)
        if isinstance(result,dA):
            newval=result.Y
        else:
            newval=result
        err = abs(newval-val)
        val = newval
        if np.all(err < tol) or np.all(err < rtol*abs(val)):
            break
    else:
        warnings.warn("maxiter (%d) exceeded in %s. Latest maximum abs. error %e and rel error = %e"
                      % (maxiter, _getFuncCode(func).co_name, err.flatten().max(), np.max(abs(err) / abs(val))), AccuracyWarning)
    if isinstance(result,dA):
        result.IntegralErr_funktEval=err,n
    return result

pQAG=parQuadratureAdaptiveGauss

def parQuadratureSimpson(funktion, lowlimit, uplimit, parname, weights=None, tol=1e-6, rtol=1e-6, dX=None, **kwargs):
    """
    Integrate a function over one of its parameters with weights using the adaptive Simpson rule.

    Integrate by adaptive Simpson integration for all .X values at once.
    Only .Y values are integrated and checked for tol criterion.
    Attributes and non .Y columns correspond to the weighted mean of parname.

    Parameters
    ----------
    funktion : function
        Function returning dataArray or array
    lowlimit,uplimit : float
        Interval borders to integrate
    parname : string
        Parname to integrate
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname e.g. a Gaussian with a<weights[0]<b and weights[1] contains weight values
        - Missing values are linear interpolated (faster). If None equal weights are used.
    tol,rtol : float, default=1e-6
        | Relative  error or absolute error to stop integration. Stop if one is full filled.
        | Tol is divided for each new interval that the sum of tol is kept.
        | .IntegralErr_funktEvaluations in dataArray contains error and number of points in interval.
    dX : float, default=None
        Minimal distance between integration points to determine a minimal step for integration variable.
    kwargs :
        Additional parameters to pass to funktion.
        If parname is in kwargs it is overwritten.

    Returns
    -------
        dataArray or array
        dataArrays have additional parameters as error and weights.

    Notes
    -----
    What is the meaning of tol in simpson method?
    If the error in an interval exceeds tol, the algorithm subdivides the interval
    in two equal parts with each :math:`tol/2` and applies the method to each subinterval in a recursive manner.
    The condition in interval i is :math:`error=|f(ai,mi)+f(mi,bi)-f(ai,bi)|/15 < tol`.
    The recursion stops in an interval if the improvement is smaller than tol.
    Thus tol is the upper estimate for the total error.

    Here we use a absolute (tol) and relative (rtol) criterion:
    :math:`|f(ai,mi)+f(mi,bi)-f(ai,bi)|/15 < rtol*fnew`
    with  :math:`fnew= ( f(ai,mi)+f(mi,bi) + [f(ai,mi)+f(mi,bi)-f(ai,bi)]/15 )` as the next improved value
    As this is tested for all .X the **worst** case is better than tol, rtol.

    The algorithm is efficient as it memoizes function evaluation at each interval border and reuses the result.
    This reduces computing time by about a factor 3-4.

    Different distribution can be found in scipy.stats. But any distribution given explicitly can be used.
    E.g. triangular np.c_[[-1,0,1],[0,1,0]].T

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import scipy
     # testcase: integrate over x of a function
     # area under normalized gaussian is 1
     js.formel.parQuadratureSimpson(js.formel.gauss,-10,10,'x',mean=0,sigma=1)
     #
     # normal distribtion of parameter D with width ds
     t=np.r_[0:150:0.5]
     D=0.3
     ds=0.1
     diff=js.dynamic.simpleDiffusion(t=t,q=0.5,D=D)
     distrib =scipy.stats.norm(loc=D,scale=ds)
     x=np.r_[D-5*ds:D+5*ds:30j]
     pdf=np.c_[x,distrib.pdf(x)].T
     diff_g=js.formel.parQuadratureSimpson(js.dynamic.simpleDiffusion,-3*ds+D,3*ds+D,parname='D',weights=pdf,tol=0.01,q=0.5,t=t)
     # compare it
     p=js.grace()
     p.plot(diff,le='monodisperse')
     p.plot(diff_g,le='polydisperse')
     p.xaxis(scale='l')
     p.legend()

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Adaptive_Simpson's_method


    """
    # We have to deal with return values as arrays and dataArrays
    if lowlimit==uplimit:
        # return function with parname=a ; to be consistent
        result=funktion(**dict(kwargs, **{parname:lowlimit}))
        if isinstance(result,dA):
            result.weightNormFactor=1
        return result
    if lowlimit>uplimit:
        lowlimit, uplimit= uplimit, lowlimit

    def _memoize(f):
        """
        avoid multiple calculations of same values at borders in each interation
        saves factor 3-4 in time
        """
        f.memo={}
        def _helper(x):
            if x not in f.memo:
                # this overwrites the kwargs[parname] with x
                Y=f(**dict(kwargs,**{parname:x}))
                if isinstance(Y,dA):         # calc the function value
                    f.memo[x]=Y.Y
                else:
                    f.memo[x]=Y
                if weights is not None:      # weigth of value
                    f.memo[x]*=np.interp(x,weights[0],weights[1])
            return f.memo[x]
        return _helper

    stack=[[lowlimit, uplimit, tol]]
    if dX is None: dX=2*(uplimit-lowlimit)
    funkt=_memoize(funktion)
    Integral=0
    Err=0
    nn=0
    # do adaptive integration
    while stack : # is not empty
        [x1,x2,err]=stack.pop()
        m=(x1+x2)/2.
        I1=(funkt(x1)+4*funkt(m)+funkt(x2))*(x2-x1)/6.  # Simpson rule.
        mleft=(x1+m)/2.
        Ileft=(funkt(x1)+4*funkt(mleft)+funkt(m))*(m-x1)/6.   # Simpson rule.
        mright=(m+x2)/2.
        Iright=(funkt(m)+4*funkt(mright)+funkt(x2))*(x2-m)/6.   # Simpson rule.
        # does the new point improve better than interval err on relative scale
        if (np.all(np.abs(Ileft+Iright-I1)<15*rtol*(Ileft+Iright+(Ileft+Iright-I1)/15.)) or \
                np.all(np.abs((Ileft+Iright-I1))<15*err)) and\
                (x2-x1) < dX:
            # good enough in this interval
            Integral+=(Ileft+Iright+(Ileft+Iright-I1)/15.)
            Err+=abs((Ileft+Iright-I1)/15.)
            nn+=1
        else:
            # split interval to improve with new points
            stack.append([x1,m,err/2])
            stack.append([m,x2,err/2])
    # calc final result with normalized weights
    if weights is not None:
        normfactor=np.trapz(weights[1],weights[0])
        parmean=np.trapz(weights[1]*weights[0],weights[0])/normfactor
    else:
        normfactor= uplimit - lowlimit
        parmean= (lowlimit + uplimit) / 2
    result=funktion(**dict(kwargs,**{parname:parmean}))
    if not isinstance(result,dA):
        print(nn)
        return Integral
    result.Y=Integral
    result.IntegralErr_funktEvaluations=max(Err),nn
    result.weightNormFactor=normfactor
    return result

pQS=parQuadratureSimpson

def simpleQuadratureSimpson(funktion, lowlimit, uplimit, parname, weights=None, tol=1e-6, rtol=1e-6, **kwargs):
    """
    Integrate a scalar function over one of its parameters with weights using the adaptive Simpson rule.

    Integrate by adaptive Simpson integration for scalar function.

    Parameters
    ----------
    funktion : function
        function to integrate
    lowlimit,uplimit : float
        interval to integrate
    parname : string
        parname to integrate
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname e.g. a Gaussian with a<weights[0]<b and weights[1] contains weight values
        - Missing values are linear interpolated (faster). If None equal weights are used.
    tol,rtol : float, default=1e-6
        | Relative  error for intervals or absolute integral error to stop integration.
    kwargs :
        additional parameters to pass to funktion
        if parname is in kwargs it is overwritten

    Returns
    -------
        float

    Notes
    -----
    What is the meaning of tol in simpson method?
    See parQuadratureSimpson.

    Examples
    --------
    ::

     distrib =scipy.stats.norm(loc=1,scale=0.2)
     x=np.linspace(0,1,1000)
     pdf=np.c_[x,distrib.pdf(x)].T
     # define function
     f1=lambda x,p1,p2,p3:js.dA(np.c_[x,x*p1+x*x*p2+p3].T)
     # calc the weighted integral
     result=js.formel.parQuadratureSimpson(f1,0,1,parname='p2',weights=pdf,tol=0.01,p1=1,p3=1e-2,x=x)
     # something simple should be 1
     js.formel.simpleQuadratureSimpson(js.formel.gauss,-10,10,'x',mean=0,sigma=1)

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Adaptive_Simpson's_method


    """
    if lowlimit==uplimit:
        # return function with parname=a ; to be consistent
        result=funktion(**dict(kwargs, **{parname:lowlimit}))
        return result
    if lowlimit>uplimit:
        lowlimit, uplimit= uplimit, lowlimit

    def _memoize(f):
        """
        avoid multiple calculations of same values at borders in each interation
        saves factor 3-4 in time
        """
        f.memo={}
        def _helper(x):
            if x not in f.memo:
                # this overwrites the kwargs[parname] with x
                Y=f(**dict(kwargs,**{parname:x}))
                if isinstance(Y,dA):Y=Y.Y
                f.memo[x]=Y
                if weights is not None:
                    f.memo[x]*=np.interp(x,weights[0],weights[1])
            return f.memo[x]
        return _helper

    stack=[[lowlimit, uplimit, tol]]
    funkt=_memoize(funktion)
    Integral=0
    Err=0
    # do adaptive integration
    while stack: # is not empty
        [x1,x2,err]=stack.pop()
        m=(x1+x2)/2.
        I1=(funkt(x1)+4*funkt(m)+funkt(x2))*(x2-x1)/6.  # Simpson rule.
        mleft=(x1+m)/2.
        Ileft=(funkt(x1)+4*funkt(mleft)+funkt(m))*(m-x1)/6.   # Simpson rule.
        mright=(m+x2)/2.
        Iright=(funkt(m)+4*funkt(mright)+funkt(x2))*(x2-m)/6.   # Simpson rule.
        # does the new point improve better than interval err on relative scale
        if np.all(np.abs(Ileft+Iright-I1)<15*rtol*(Ileft+Iright+(Ileft+Iright-I1)/15.)) or \
           np.all(np.abs((Ileft+Iright-I1))<15*err):
            # good enough in this interval
            Integral+=(Ileft+Iright+(Ileft+Iright-I1)/15.)
            Err+=abs((Ileft+Iright-I1)/15.)
        else:
            # split interval to improve with new points
            stack.append([x1,m,err/2])
            stack.append([m,x2,err/2])
    return Integral

sQS=simpleQuadratureSimpson

def convolve(A,B,mode='same',normA=False,normB=False):
    r"""
    Convolve A and B  with proper tracking of the output X axis.

    Approximate the convolution integral as the discrete, linear convolution of two one-dimensional sequences.
    Missing values are linear interpolated to have matching steps. Values outside of X ranges are set to zero.


    Parameters
    ----------
    A,B : dataArray, ndarray
        To be convolved arrays (length N and M).
         - dataArray convolves Y with Y values
         - ndarray A[0,:] is X and A[1,:] is Y
    normA,normB : bool, default False
        Determines if A or B should be normalised that :math:`\int_{x_{min}}^{x_{max}} A(x) dx = 1`.
    mode : 'full','same','valid', default 'same'
        See example for the difference in range.
        - 'full'  Returns the convolution at each point of overlap, with an output shape of (N+M-1,).
                  At the end-points of the convolution, the signals do not overlap completely, and boundary effects may be seen.
        - 'same'  Returns output of length max(M, N). Boundary effects are still visible.
        - 'valid' Returns output of length M-N+1.

    Returns
    -------
        dataArray (with attributes from A)

    Notes
    -----
     - :math:`A\circledast B (t)= \int_{-\infty}^{\infty} A(x) B(t-x) dx = \int_{x_{min}}^{x_{max}} A(x) B(t-x) dx`
     - If A,B are only 1d array use np.convolve.
     - If attributes of B are needed later use .setattr(B,'B_') with prependen 'B_' for b attributes.

    Examples
    --------
    Demonstrate the difference between modes::

     import jscatter as js;import numpy as np
     s1=3;s2=4;m1=50;m2=10
     G1=js.formel.gauss(np.r_[0:100.1:0.1],mean=m1,sigma=s1)
     G2=js.formel.gauss(np.r_[-30:30.1:0.2],mean=m2,sigma=s2)
     p=js.grace()
     p.title('Convolution of Gaussians (width s mean m)')
     p.subtitle('s1\S2\N+s2\S2\N=s_conv\S2\N ;  m1+m2=mean_conv')
     p.plot(G1,le='mean 50 sigma 3')
     p.plot(G2,le='mean 10 sigma 4')
     ggf=js.formel.convolve(G1,G2,'full')
     p.plot(ggf,le='full')
     gg=js.formel.convolve(G1,G2,'same')
     p.plot(gg,le='same')
     gg=js.formel.convolve(G1,G2,'valid')
     p.plot(gg,le='valid')
     gg.fit(js.formel.gauss,{'mean':40,'sigma':1},{},{'x':'X'})
     p.plot(gg.modelValues(),li=1,sy=0,le='fit m=$mean s=$sigma')
     p.legend(x=100,y=0.1)
     p.xaxis(max=150,label='x axis')
     p.yaxis(min=0,max=0.15,label='y axis')

    References
    ----------
    .. [1] Wikipedia, "Convolution", http://en.wikipedia.org/wiki/Convolution.

    """
    # convert to array
    if hasattr(A,'_isdataArray'):
        AY=A.Y
        AX=A.X
    else:
        AX=A[0,:]
        AY=A[1,:]
    if normA:
        AY=AY/np.trapz(AY,AX)
    if hasattr(B,'_isdataArray'):
        BY=B.Y
        BX=B.X
    else:
        BX=B[0,:]
        BY=B[1,:]
    if normB:
        BY=BY/np.trapz(BY,BX)
    # create a combined x scale
    dx=min(np.diff(AX).min(),np.diff(BX).min())
    ddx=0.1*dx # this accounts for the later >= BX.min() to catch problems with numerical precision
    XX=np.r_[min(AX.min(),BX.min()):max(AX.max(),BX.max())+dx:dx]
    # interpolate missing values
    #if x scale is equal this is nearly no overhead
    AXX = XX[(XX >= AX.min()-ddx) & (XX <= AX.max()+ddx)]
    AY_xx = np.interp(AXX, AX, AY, left=0, right=0)
    BXX = XX[(XX >= BX.min()-ddx) & (XX <= BX.max()+ddx)]
    BY_xx = np.interp(BXX, BX, BY, left=0, right=0)
    if len(AXX)<len(BXX):
        # AXX always the larger one; this is also done in C source
        AXX,BXX=BXX,AXX
    # convolve
    res = np.convolve(AY_xx, BY_xx, mode=mode) * dx
    # define x scale
    # n,nleft,nright,length to reproduce C-source of convolve
    n=BXX.shape[0]
    l=AXX.shape[0]
    xx = np.r_[AX.min() + BX.min():AX.max() + BX.max()+dx:dx]
    if mode=='full':       # length=l+n-1
        nleft=0
        nright=l+n-1
    elif mode=='valid':    # length=l-n+1
        nleft=n-1
        nright=l
    else: # mode=='same'  # length=l
        nleft=(n-1)//2
        nright=nleft+l
    xx=xx[nleft:nright]
    result=dA(np.c_[xx,res].T)
    result.setattr(A)
    return result

def sphereAverage(function,relError=300,*args,**kwargs):
    """
    Spherical average - non-parallel

    A Fibonacci lattice on a sphere or Monte Carlo is used.

    Parameters
    ----------
    function : function
        Function to evaluate returning a list of return values (all are integrated)
        function  gets cartesian coordinate of point on unit sphere as first argument
    relError : float, default 300
        Determines how points on sphere are selected
         - >1  Fibonacci Lattice with relError*2+1 points
         - 0<1 Random points on sphere (Monte Carlo integration).
               Stops if relative improvement in mean is less than relError.
               Final error is (stddev of N points) /sqrt(N) as for Monte Carlo methods
               even if it is not a correct 1-sigma error in this case.
    args,kwargs :
        Forwarded to function

    Returns
    -------
    array like :
        Values from function and appended Monte Carlo error estimates.

    Examples
    --------
    ::

     def f(x,r):
        return [js.formel.xyz2rphitheta(x)[1:].sum()*r]
     js.formel.sphereAverage(f,relError=500,r=1)


    """
    if relError<0:
        relError=abs(relError**-2)
    if 0<relError<1:
        points=rphitheta2xyz(parallel.randomPointsN(100))
        results=np.r_[[np.array(function(point,*args,**kwargs),ndmin=1)  for point in points]]
        lastmean= results.mean(axis=0).real
        while 1:
            points=rphitheta2xyz(parallel.randomPointsN(40))
            result=np.r_[[np.array(function(point,*args,**kwargs),ndmin=1)  for point in points]]
            results=np.r_[results,np.array(result,ndmin=1)]
            mean=results.mean(axis=0).real
            if np.all(abs(1-lastmean/mean)<relError):
                break
            else:
                lastmean=mean
    elif relError>1:
        qfib=fibonacciLatticePointsOnSphere(relError,1)
        points=rphitheta2xyz(qfib)    # to cartesian
        results=np.r_[[np.array(function(point,*args,**kwargs),ndmin=1)  for point in points]]
    return np.r_[results.mean(axis=0),results.std(axis=0)/np.sqrt(np.shape(results[0])[0])]

#: parallel sphereAverage; see :func:`parallel.psphereAverage`
psphereAverage=parallel.psphereAverage

def parDistributedAverage(funktion, sig, parname, type='normal', nGauss=30, **kwargs):
    """
    Average a function assuming a parameter is distributed with width sig.

    Function average over a parameter with weights determined from probability distribution.
    Adaptive integration over given distribution or summation with weights is used.

    Parameters
    ----------
    funktion : function
        Function to integrate with distribution weight.
        Function needs to return dataArray.
    sig : float
        width parameter of the  distribution, see Notes
    parname : string
        Name of the parameter of funktion which shows a distribution
    type : 'normal','lognorm','gamma','lorentz','uniform','poisson' default 'normal'
        Type of the distribution
    kwargs : parameters
       Any additonal kword parameter to pass to function.
       The value of parname will be the mean value of the distribution.
    nGauss : float , default=30
        Order of quadrature integration as number of intervals in Gauss–Legendre quadrature over distribution.
        Distribution is integrated in probability interval [0.001..0.999].

    Returns
    -------
    dataArray :
        as returned from function for mean value
        | with .parname_mean = mean of parname
        |      .parname_std  = standard deviation of parname

    Notes
    -----
    The used distributions are from scipy.stats.
    Choose the distribution according to the problem.
    
    mean is the value in kwargs[parname]. mean and sig are used as:

    * norm :
        | mean , std
        | stats.norm(loc=mean,scale=sig)
    * lognorm :
        | mean and sig evaluate to mean and std
        | mu=math.log(mean**2/(sig+mean**2)**0.5)
        | nu=(math.log(sig/mean**2+1))**0.5
        | stats.lognorm(s=nu,scale=math.exp(mu))
    * gamma :
        | mean and sig evaluate to mean and std
        | stats.gamma(a=mean**2/sig**2,scale=sig**2/mean)
    * lorentz = cauchy:
        | mean and std are not defined. Use FWHM instead to describe width.
        | sig=FWHM
        | stats.cauchy(loc=mean,scale=sig))
    * uniform :
        | sig is width
        | stats.uniform(loc=mean-sig/2.,scale=sig))
    * poisson:
        stats.poisson(mu=mean,loc=sig)

    For more distribution look into this source code and use it appropriate with scipy.stats.

    Examples
    --------
    ::

     import jscatter as js
     p=js.grace()
     q=js.loglist(0.1,5,500)
     sp=js.ff.sphere(q=q,radius=5)
     p.plot(sp,sy=[1,0.2],legend='single radius')
     p.yaxis(scale='l',label='I(Q)')
     p.xaxis(scale='n',label='Q / nm')
     sig=0.2
     p.title('radius distribution with width %.g' %(sig))
     sp2=js.formel.pDA(js.ff.sphere,sig,'radius',type='normal',q=q,radius=5,nGauss=100)
     p.plot(sp2,li=[1,2,2],sy=0,legend='normal 100 points Gauss ')
     sp4=js.formel.pDA(js.ff.sphere,sig,'radius',type='normal',q=q,radius=5,nGauss=30)
     p.plot(sp4,li=[1,2,3],sy=0,legend='normal 30 points Gauss  ')
     sp5=js.formel.pDA(js.ff.sphere,sig,'radius',type='normal',q=q,radius=5,nGauss=5)
     p.plot(sp5,li=[1,2,5],sy=0,legend='normal 5 points Gauss  ')
     sp3=js.formel.pDA(js.ff.sphere,sig,'radius',type='lognormal',q=q,radius=5)
     p.plot(sp3,li=[3,2,4],sy=0,legend='lognormal')
     sp6=js.formel.pDA(js.ff.sphere,sig,'radius',type='gamma',q=q,radius=5)
     p.plot(sp6,li=[2,2,6],sy=0,legend='gamma ')
     # an unrealistic example
     sp7=js.formel.pDA(js.ff.sphere,1,'radius',type='poisson',q=q,radius=5)
     p.plot(sp7,li=[1,2,6],sy=0,legend='poisson ')
     p.legend()

    """
    mean=kwargs[parname]
    # define the distribution with parameters
    if type=='poisson':
        distrib=stats.poisson(mu=mean,loc=sig)
    elif type=='lognorm':
        mu=math.log(mean**2/(sig+mean**2)**0.5)
        nu=(math.log(sig/mean**2+1))**0.5
        distrib=stats.lognorm(s=nu,scale=math.exp(mu))
    elif type=='gamma':
        distrib=stats.gamma(a=mean**2/sig**2,scale=sig**2/mean)
    elif type=='lorentz' or type=='cauchy':
        distrib=stats.cauchy(loc=mean,scale=sig)
    elif type=='uniform':
        distrib=stats.uniform(loc=mean-sig/2.,scale=sig)
    else:# type=='norm'  default
        distrib=stats.norm(loc=mean,scale=sig)

    # get starting and end values for integration
    a=distrib.ppf(0.001)
    b=distrib.ppf(0.999)
    if type in 'poisson':
        # discrete distributions
        result=dL()
        x=range(int(a),int(b+1))
        w=distrib.pmf(x)
        for xi,wi in zip(x,w):
            result.append(funktion(**dict(kwargs,**{parname:xi})))
            result[-1].Y*=wi
        result[0].Y=result.Y.array.sum(axis=0)/w.sum()
        result=result[0]
    else :
        # here we use the fixedGauss for integration
        x=np.linspace(a,b,1000)
        pdf=np.c_[x,distrib.pdf(x)].T
        # calc the weighted integral
        result=parQuadratureFixedGauss(funktion, a, b, parname=parname, n=nGauss, weights=pdf, **kwargs)
        result.Y/=result.weightNormFactor

    # calc mean and std and store in result
    setattr(result,parname+'_mean',distrib.mean())
    setattr(result,parname+'_std',distrib.std())
    if type=='lorentz' or type=='cauchy':
        setattr(result,parname+'_FWHM',2*sig)

    return result

pDA=parDistributedAverage

def viscosity(mat='h2o',T=293.15):
    """
    Viscosity of pure solvents. For buffer solvents use bufferviscosity.

    Parameters
    ----------
    mat : string  'h2o','d2o','toluol','methylcyclohexan',  default h2o
        Solvent
    T : float
        Temperature T in Kelvin  default 293K

    Returns
    -------
    float :    viscosity in Pa*s
        water H2O ~ 0.001 Pa*s =1 cPoise             # Poise=0.1 Pa*s

    References
    ----------
    .. [1]  The Viscosity of Toluene in the Temperature Range 210 to 370 K
            M. J. Assael, N.K. Dalaouti, J.H., Dymond International Journal of Thermophysics, Vol. 21,291  No. 2, 2000
            #  accuracy +- 0.4 % laut paper Max error von Experiment data

    .. [2] Thermal Offset Viscosities of Liquid H2O, D2O, and T2O
           C. H. Cho, J. Urquidi,  S. Singh, and G. Wilse Robinson  J. Phys. Chem. B 1999, 103, 1991-1994


    """
    temp=T
    if re.match('^'+mat,'toluol'):
        # print 'Material Toluol  Temperatur', temp , ' Viscosity in mPas (=cP)   ',
        Tc,ck0,ck1,ck2,ck3,ck4=591.75,34.054,-219.46,556.183,-653.601,292.762 # critical temperature and coefficients
        T=temp/Tc
        vis29315=0.0005869    # Pas
        vis=vis29315*math.exp(ck0+ck1*T+ck2*T*T+ck3*T*T*T+ck4*T*T*T*T)
        return vis*1000
    elif re.match('^'+mat,'methylcyclohexan'):
        # print 'Material  Methylcyclohexan Temperatur', temp , ' Viscosity in mPas (=cP)'
        vis=0.001*math.exp(-4.48+1217./temp)
        return vis*1000
    elif re.match('^'+mat,'d2o'):
        # print 'Material D2O  Temperatur', temp , ' Viscosity in mPas (=cP)   ',
        T0=231.832   # reference Temperature
        ck0=0.0
        ck1=1.0
        ck2=2.7990E-3      # Koeffizienten
        ck3=-1.6342E-5
        ck4=2.9067E-8
        gamma=1.55255
        dT=temp-T0
        vis231832=885.60402    # cPK^gamma
        vis=vis231832*(ck0+ck1*dT+ck2*dT**2+ck3*dT**3+ck4*dT**4)**(-gamma)
        # print vis
        return vis*1e-3
    else:
        # print 'Material H2O  Temperatur', temp , ' Viscosity in mPas (=cP)   ',
        T0=225.334   # reference Temperature
        ck0=0.0
        ck1=1.0
        ck2=3.4741E-3      # Koeffizienten
        ck3=-1.7413E-5
        ck4=2.7719E-8
        gamma=1.53026
        dT=temp-T0
        vis225334=802.25336    # cPK^gamma
        vis=vis225334*1/((ck0+ck1*dT+ck2*dT**2+ck3*dT**3+ck4*dT**4)**gamma)
        # print vis
        return vis*1e-3

def _convertfromUltrascan():
    """
    Internal usage to document how bufferComponents.txt was generated
    Get xml file from ultrascan and convert to ascii file to read on module load (faster than xmltree)

    We use only the fields we need here.

    """
    import xml.etree.ElementTree
    buffers = xml.etree.ElementTree.parse('bufferComponents.xml').getroot()
    bl=[] # new bufferlines
    bl+=['# buffer coefficients for density (dci) and viscosity (vci) as read from Ultrascan 3 '+'\n']
    content=['name']+['dc0','dc1','dc2','dc3','dc4','dc5']+['vc0','vc1','vc2','vc3','vc4','vc5']+['unit','range']
    bl+=['# '+' '.join(content)+'\n']
    for buff in buffers:
        name=buff.attrib['name'].title().replace(' ','').replace('-','')
        if name[0].isdigit():name=name[1:]+name[0]
        line=[name]
        line += [buff[0].attrib[attrib] for attrib in ['c0','c1','c2','c3','c4','c5']]
        line += [buff[1].attrib[attrib] for attrib in ['c0', 'c1', 'c2', 'c3', 'c4', 'c5']]
        line += [buff.attrib[attrib].strip().replace(' ', '_') for attrib in ['unit', 'range']]
        bl+=[' '.join(line)+'\n']
    bl.sort()
    with io.open(_path_+'/bufferComponents.txt','w') as _f:
        _f.writelines(bl)

def bufferviscosity(composition,T=293.15,showvalidity=False):
    """
    Viscosity of water with inorganic substances as used in biological buffers.

    Solvent with composition of H2O and D2O  and additional components at temperature T.
    Ternary solutions allowed. Units are mol; 1l h2o = 55.50843 mol
    Based on data from ULTRASCAN3 [1]_ supplemented by the viscosity of H2O/D2O mixturees for conc=0.

    Parameters
    ----------
    composition : list of compositional strings
        | Compositional string of chemical name as 'float'+'name'
        | First float is content in Mol followed by component name as
        | 'h2o' or 'd2o' light and heavy water were mixed with prepended fractions.
        | ['1.5urea','0.1sodiumchloride','2h2o' or '1d2o']
        | for 1.5 M urea + 100 mM NaCl in a 2:1 mixture of h2o/d2o.
        | By default '1h2o' is assumed.
    T : float, default 293.15
        Temperature in K
    showvalidity : bool, default False
        Show validity range of components.

    Returns
    -------
        float viscosity in Pa*s

    Notes
    -----
    - Viscosities of H2O/D2O mixtures mix by linear interpolation between concentrations (accuracy 0.2%) [2]_.
    - The change in viscosity due to components is added based on data from Ultrascan3 [1]_.
    - Multicomponent mixtures are composed of binary mixtures.
    - Glycerol%" is in unit "%weight/weight" for range="0-32%, here the unit is changed to weight% insthead of M.
    - Propanol1, Propanol2 are 1-Propanol, 2-Propanol


    References
    ----------
    .. [1] http://www.ultrascan3.uthscsa.edu/
    .. [2] Viscosity of light and heavy water and their mixtures
           Kestin Imaishi Nott Nieuwoudt Sengers, Physica A: Statistical Mechanics and its Applications 134(1):38-58
    .. [3] Thermal Offset Viscosities of Liquid H2O, D2O, and T2O
           C. H. Cho, J. Urquidi,  S. Singh, and G. Wilse Robinson  J. Phys. Chem. B 1999, 103, 1991-1994

    availible components::

     h2o1 d2o1
    """
    if isinstance(composition,str):
        composition=[composition]
    cd2o=0
    ch2o=0
    nwl={}  # nonwaterlist
    # decompose composition
    for compo in composition:
        compo=compo.lower()
        decomp=re.findall('\d+\.\d+|\d+|\D+',compo)
        if not re.match('\d',decomp[0]):
            raise KeyError('Component %s missing concentration ' %compo)
        component=''.join(decomp[1:])
        conc=float(decomp[0])                           # in Mol
        if component in ['h2o1','h2o' ]:
            ch2o+=conc
        elif component in ['d2o1','d2o']:
            cd2o+=conc
        else:
            nwl[component]=(conc,)+(_bufferDensityViscosity[component][6:14])
    if ch2o==0 and cd2o==0:
        # default if no water composition was given
        ch2o=1 #
    # temperature dependent viscosity of h20/d2o mixture as basis in mPas (Ultrascan units)
    visc=(ch2o*viscosity(mat='h2o',T=T)+cd2o*viscosity(mat='d2o',T=T))/(ch2o+cd2o)*1000.
    # coefficints all for c=0 give water viscosity (which is not always correct!!)
    # coefficients[i>0] give increase from conc =0
    #  so add them up
    vc=np.r_[0.].repeat(6)                            # sum coefficients
    ff=np.r_[1.,1e-3,1e-2,1e-3,1e-4,1e-6]             # standard powers
    for k,v in nwl.items():
        c=v[0];coefficients=v[1:7];range=v[8]         # concentration (converted to mM) and coefficients
        cp=np.r_[0,c**0.5,c,c*c,c**3,c**4]            # concentration powers
        if showvalidity:
            print(k,' : ',range)
        vc+=coefficients*cp
    visc=visc+np.sum(vc*ff)                           # multiply by standard powers
    return visc/1000.                                 # return use Pa*s

# complete the docstring from above
_avlist=sorted(_bufferDensityViscosity.keys())
_i=0
while _i<len(_avlist):
    bufferviscosity.__doc__+='     '+''.join([' %-25s'%cc for cc in _avlist[_i:_i+3]])+'\n'
    _i+=3
bufferviscosity.__doc__+='\n'

def waterdensity(composition,T=293.15,units='mol',showvalidity=False):
    """
    Density of water with inorganic substances (salts).

    Solvent with composition of H2O and D2O  and additional inorganic components at temperature T.
    Ternary solutions allowed. Units are mol; 1l h2o = 55.50843 mol

    Parameters
    ----------
    composition : list of compositional strings
        | Compositional string of chemical formula as 'float'+'chemical char' + integer
        | First float is content in mol (is later normalised to sum of contents)
        | chemical letter + number of atoms in formula (single atoms append 1 ,fractional numbers allowed)
        | e.g.
        | 'h2o1' or 'd2o1' light and heavy water with 'd1' for deuterium
        | 'c3h8o3' or 'c3h1d7o3' partial deuterated glycerol
        | ['55.55h2o','2.5Na1Cl1'] for 2.5 mol NaCl added to  1l h2o (55.55 mol)
        | ['20H2O1','35.55D2O1','0.1Na1Cl1'] h2o/d2o mixture with 100mMol NaCl
    units : default='mol'
        Anything except 'mol' unit is mass fraction
        'mol' units is mol and mass fraction is calculated as mass=[mol]*mass_of_molecule
        e.g. 1l Water with 123mM NaCl   ['55.5H2O1','0.123Na1Cl1']
    T : float, default=293.15
        temperature in K
    showvalidity : bool, default False
        Show additionally validity range for temperature and concentration according to [4]_.
        - Temperature range in °C
        - concentration in wt % or up to a saturated solution (satd)
        - error in 1/100 % see [4]_.

    Returns
    -------
    float in g/ml

    Notes
    -----
    - D2O maximum density 1.10596 at T=273.15+11.23 K [1]_ .
    - For mixtures of H2O/D2O molar volumes add with an accuracy of about 2e-4 cm**3/mol
      compared to 18 cm**3/mol molar volume [3]_.
    - Additional densities of binary aqueous solutions [4]_.

    References
    ----------
    .. [1] The dilatation of heavy water
           K. Stokland, E. Ronaess and L. Tronstad Trans. Faraday Soc., 1939,35, 312-318 DOI: 10.1039/TF9393500312
    .. [2] Effects of Isotopic Composition, Temperature, Pressure, and Dissolved Gases on the Density of Liquid Water
           George S. Kell JPCRD 6(4) pp. 1109-1131 (1977)
    .. [3] Excess volumes for H2O + D2O liquid mixtures
           Bottomley G Scott R  Australian Journal of Chemistry 1976 vol: 29 (2) pp: 427
    .. [4] Densities of binary aqueous solutions of 306 inorganic substances
           P. Novotny, O. Sohnel  J. Chem. Eng. Data, 1988, 33 (1), pp 49–55   DOI: 10.1021/je00051a018

    availible components::

     h2o1 d2o1
     TRIS c4h11n1o3
     TABS c8h19n1o6s1

    """
    mw=18.01528 # mol weight water
    T-=273.15
    wdensity=lambda T,a0,a1,a2,a3,a4,a5,b:(a0+a1*T+a2*T**2+a3*T**3+a4*T**4+a5*T**5)/(1+b*T)/1000.
    # 5-100 °C
    # D2O max density 1.10596 at T=11,23°C from Stokeland Trans. Faraday Soc., 1939,35, 312-31
    # we use here 1104.633 instead of the original 1104.7056 of Kell to get the max density correct
    cD2O=[1104.633,28.88152,-7.652899e-3,-136.61854e-6,534.7350e-9,-1361.843e-12,25.91488e-3]
    # 0-150 K
    cH2O=[999.84252,16.945227,-7.9870641e-3,-46.170600e-6,105.56334e-9,-280.54337e-12,16.879850e-3]

    # additional density due to added inorganic components
    def _getadddensity(c,TT,decompp):
        pp=_aquasolventdensity[decompp]
        if decompp=='c4h11n1o3':
            return pp[0]*c**pp[1]
        elif decompp=='c8h19n1o6s1':
            return pp[0]*c**pp[1]
        else:
            if showvalidity:
                print(decompp,': Temperaturerange: ',pp[7],' concentration: ',pp[8],' error %:',pp[6])
            return (pp[0]*c+pp[1]*c*TT+pp[2]*c*TT*TT+pp[3]*c**(3/2.)+pp[4]*c**(3/2.)*TT+pp[5]*c**(3/2.)*TT*TT)*1e-3

    cd2o=0
    ch2o=0
    nonwaterlist={}
    adddensity=0
    if isinstance(composition,str):
        composition=[composition]
    for compo in composition:
        compo=compo.lower()
        decomp=re.findall('\d+\.\d+|\d+|\D+',compo)
        if not re.match('\d',decomp[0]): # add a 1 as concentration in front if not there
            decomp=[1]+decomp
        if not re.match('\d+\.\d+|\d+',decomp[-1]):
            raise KeyError('last %s Element missing following number '%decomp[-1])
        mass=np.sum([Elements[ele][1]*float(num) for ele,num in zip(decomp[1:][::2],decomp[1:][1::2])])
        if units.lower()!='mol':
            # we convert here from mass to mol
            concentration=float(decomp[0])/mass
        else:
            concentration=float(decomp[0])  # concentration of this component
        decomp1=''.join(decomp[1:])
        if decomp1=='h2o1':
            ch2o+=concentration
        elif decomp1=='d2o1':
            cd2o+=concentration
        else:
            nonwaterlist[decomp1]=concentration
    wff=(1000/mw)/(ch2o+cd2o)
    for k,v in nonwaterlist.items():
        # additional density due to components
        adddensity+=_getadddensity(v*wff,T,k)
    density=cd2o/(cd2o+ch2o)*wdensity(T,cD2O[0],cD2O[1],cD2O[2],cD2O[3],cD2O[4],cD2O[5],cD2O[6])
    density+=ch2o/(cd2o+ch2o)*wdensity(T,cH2O[0],cH2O[1],cH2O[2],cH2O[3],cH2O[4],cH2O[5],cH2O[6])
    return density+adddensity

# complete the docstring from above
_aqlist=sorted(_aquasolventdensity.keys())
_i=0
while _i<len(_aqlist):
    waterdensity.__doc__+='     '+''.join([' %-12s'%cc for cc in _aqlist[_i:_i+6]])+'\n'
    _i+=6
waterdensity.__doc__+='\n'

def scatteringLengthDensityCalc(composition,density=None,T=293,units='mol',mode='all'):
    """
    Scattering length density for water mixtures for xrays and neutrons.

    Scattering length density for binary water mixtures from water density and
    mass fraction or mol concentration of composition (see Notes for available components).

    Parameters
    ----------
    density : float, default=None
        density in g/cm**3 = g/ml
        if not given function waterdensity is tried to calculate the solution density with inorganic components
        in this case 'h2o1' and/or 'd2o1' need to be in composition
        otherwise measure by weighting a volume from pipette (lower accuracy) or densiometry (higher accuracy)
    composition : list of concentration + chemical formula
        | a string with chemical formula as letter + number and prepended concentration in mol
        | ['10H2O1','0.5D2O1'] mixture of heavy and light water
        | '0.1C3H8O3' or '0.1C3H1D7O3' for glycerol with 'D' for deuterium
        | if one atom append 1 to avoid confusion
        | fractional numbers allowed, but think of meaning (Isotope mass fraction??)
        | if composition is a list of strings preceded by mass fraction or concentration in mol of component
        | eg ['1.0h2o','0.1c3h8o3'] for 10% mass glycerol added to  100% h2o and units='mass'
        |    ['55000H2O1','50Na3P1O4','137Na1Cl1'] for a 137mMol NaCl +50mMol Phophate H2O buffer 
        |    remember to adjust density
    units : 'mol'
        anything except 'mol' prepended unit is mass fraction (default)
        'mol' prepended units is mol and mass fraction is calculated as mass=[mol]*mass_of_molecule
        e.g. 1l Water with 123mmol NaCl   ['55.5H2O1','0.123Na1Cl1']
    mode
        | 'xsld'      return xray scattering length density       in  nm**-2
        | 'edensity'  return electron density                     in e/nm**3
        | 'ncohsld'   return coherent scattering length density   in  nm**-2
        | 'incsld'    return incoherent scattering length density in  nm**-2
        | 'all'       return xsld,edensity,nsld,incsld,mass,massfullprotonated,massfulldeuterated,d2o/h2o_fraction
    T : float, default=293
        temperature in °K

    Returns 
    -------
    float or list of float corresponding to mode
    
    Notes
    -----
    | edensity=be*massdensity/weigthpermol*sum_atoms(numberofatomi*chargeofatomi)
    | be = scattering length electron =µ0*e**2/4/pi/m=2.8179403267e-6nm
    | mass,massfullprotonated,massfulldeuterated are the sum of the molecules each counted once
    | in mode 'all' the masses can be used to calc the deuterated density if same volume is assumed.
    | e.g.  fulldeuterated_density=protonated_density/massfullprotonated*massfulldeuterated

    For density reference see waterdensity.

    """
    edensity=[]
    bcdensity=[]
    bincdensity=[]
    total=0
    totalmass=0
    d2o=0
    h2o=0
    massfullprotonated=0
    massfulldeuterated=0
    if not isinstance(density,(float,int,np.ndarray)):
        density=waterdensity(composition,T=T,units=units)
    density=float(density)
    if isinstance(composition,str):
        composition=[composition]
    for compo in composition:
        compo=compo.lower()
        # decompose in numbers and characters
        decomp=re.findall('\d+\.\d+|\d+|\D+',compo)
        if not re.match('\d',decomp[0]): # add a 1 as concentration in front if not there
            decomp=[1]+decomp
        mass=np.sum([Elements[ele][1]*float(num) for ele,num in zip(decomp[1:][::2],decomp[1:][1::2])])
        if units.lower() is 'mol':
            ##if units=mol we convert here from mol to mass fraction
            massfraction=float(decomp[0])*mass
        else:
            massfraction=float(decomp[0])
        sumZ=0
        b_coherent=0
        b_incoherent=0
        # check for completeness at end
        if not re.match('\d+\.\d+|\d+',decomp[-1]):
            raise KeyError('last %s Element missing following number '%decomp[-1])
        for ele,num in zip(decomp[1:][::2],decomp[1:][1::2]):
            if ele in Elements.keys():
                num=float(num)
                sumZ+=Elements[ele][0]*num
                massfullprotonated+=(Elements['h'][1]*num) if ele in ['h','d'] else (Elements[ele][1]*num)
                massfulldeuterated+=(Elements['d'][1]*num) if ele in ['h','d'] else (Elements[ele][1]*num)
                b_coherent+=Elements[ele][2]*num
                b_incoherent+=Elements[ele][3]*num
            else:
                print('decomposed to \n',decomp)
                raise KeyError('"%s" not found in Elements'%ele)

        # density[g/cm^3] / mass[g/mol]= N in mol/cm^3 --> N*Z is charge density
        if ''.join(decomp[1:])=='h2o1': h2o+=massfraction
        if ''.join(decomp[1:])=='d2o1': d2o+=massfraction
        edensity.append(massfraction*density*(constants.N_A/1e21)/mass*sumZ)
        bcdensity.append(massfraction*density*(constants.N_A/1e21)/mass*b_coherent)
        bincdensity.append(massfraction*density*(constants.N_A/1e21)/mass*b_incoherent)
        totalmass+=mass
        total+=massfraction
    if mode[0]=='e':
        return sum(edensity)/total
    elif mode[0]=='x':
        return sum(edensity)/total*felectron
    elif mode[0]=='n':
        return sum(bcdensity)/total
    elif mode[0]=='i':
        return sum(bincdensity)/total
    else:
        return sum(edensity)/total*felectron,\
               sum(edensity)/total,\
               sum(bcdensity)/total,\
               sum(bincdensity)/total,\
               totalmass,\
               massfullprotonated,\
               massfulldeuterated,\
               d2o/(h2o+d2o) if h2o+d2o!=0 else 0

def watercompressibility(d2ofract=1,T=278,units='MMTK'):
    """
    Isothermal compressibility of H2O and D2O mixtures with d2o fraction in solvent.

    Parameters
    ----------
    d2ofract : float, default 1
        Fraction d2o
    T : float, default 278K
        Temperature  in K
    units : string 'MMTK'
        MMTK units  ps, nm, g/mol

    Returns
    -------
    Compressibility in units of 'MMTK' -> ps^2*nm/(g/mol) or in 1/bar.
    Linear mixture according to d2ofract.

    Notes
    -----
    To get kT*compressibility =compr*k_B/Nav*300/cm**3    in  hwater 1.91e-24 cm**3 at 20°C

    References
    ----------
    .. [1] Isothermal compressibility of Deuterium Oxide at various Temperatures
          Millero FJ and Lepple FK   Journal of chemical physics 54,946-949 (1971)   http://dx.doi.org/10.1063/1.1675024
    .. [2] Precise representation of volume properties of water at one atmosphere
          G. S. Kell J. Chem. Eng. Data, 1967, 12 (1), pp 66–69  http://dx.doi.org/10.1021/je60032a018

    """
    t=T-273.15
    h2o=lambda t:1e-6*(50.9804-0.374957*t+7.21324e-3*t**2-64.1785e-6*t**3+0.343024e-6*t**4-0.684212e-9*t**5)
    d2o=lambda t:1e-6*(53.61-0.4717*t+0.009703*t**2-0.0001015*t**3+0.0000005299*t**4)

    comp_1overbar=d2ofract*d2o(t)+(1-d2ofract)*h2o(t)
    # MMTK units  ps, nm, g/mol
    if units=='MMTK':
        # factor=1e-8*m*s**2/(g/Nav)
        factor=1e-8*1e9*1e12**2# /(6.0221366999999997e+23/6.0221366999999997e+23)
    else:
        factor=1
    compressibility_MMTKUnits=comp_1overbar*factor
    return compressibility_MMTKUnits

def dielectricConstant(material='d2o',T=293.15,conc=0,delta=5.5):
    """
    Dielectric constant of H2O and D2O buffer solutions.
    
    Dielectric constant of H2O and D2O (error +- 0.02) with added buffer salts.
    
    Parameters
    ----------
    material : string 'd2o' (default)   or 'h2o'
        material 'd2o' (default)   or 'h2o'
    T : float
        temperature in °C
    conc : float
        the salt concentration in mol/l
    delta : float 
        the total excess polarisation dependent on the salt and presumably on the temperature!
        eps(c)=eps(c=0)+2*delta*c    for c<2M

    Returns
    -------
    float : dielectric constant

    Notes
    -----
    ======  ========== ===========================
    Salt    delta(+-1) deltalambda (not used here)
    ======  ========== ===========================
    HCl     -10            0
    LiCI     7            -3.5
    NaCI     5.5          -4   default
    KCl      5            -4
    RbCl     5            -4.5
    NaF      6            -4
    KF       6.5          -3.5
    NaI     -7.5          -9.5
    KI      -8            -9.5
    MgCI,   -15           -6
    BaCl2   -14           -8.5
    LaCI.   -22           -13.5
    NaOH    -10.5         -3
    Na2SO.  -11           -9.5
    ======  ========== ===========================

    References
    ----------
    .. [1] The dielectric constant of water and heavy water between 0 and 40.degree.
          J. Phys. Chem., 1967, 71 (3), pp 656–662   http://dx.doi.org/10.1021/j100862a028
    .. [2] Dielectric Constant of Deuterium Oxide
          C.G Malmberg, Journal of Research of National Bureau of Standards, Vol 60 No 6, (1958) 2874
          http://nvlpubs.nist.gov/nistpubs/jres/60/jresv60n6p609_A1b.pdf
    .. [3] Dielectric Properties of Aqueous Ionic Solutions. Parts I and II
          Hasted et al. J Chem Phys 16 (1948) 1   http://link.aip.org/link/doi/10.1063/1.1746645

    """
    if material=='h2o':
        diCo=lambda t:10**(1.94404-1.991e-3*T)
        return diCo(T)+2*delta*conc
    elif material=='d2o':
        diCo=lambda t:87.48-0.40509*(t-273.15)+9.638e-4*(t-273.15)**2-1.333e-6*(t-273.15)**3
    return diCo(T)+2*delta*conc

###################################################

def cstar(Rg,Mw):
    """
    Overlapp concentration for a polymer

    Parameters
    ----------
    Rg : float  in nm
        radius of gyration 
    Mw : float
        molecular weight

    Returns
    -------
    concentration % w/vol for D2O
    """
    cstar=Mw/(constants.Avogadro*4./3.*math.pi*(Rg*1E-9)**3)/1000  # in g/l
    return cstar

def Dtrans(Rh,Temp=273.15,solvent='h2o',visc=None):
    """
    Translational diffusion for a sphere

    Parameters
    ----------
    Rh : float
        hydrodynamic radius in nm
    Temp : float
        temperature   in K
    solvent : float
        like in viscosity; used if visc==None 
    visc : float
        viscosity in Pa*s  =>    H2O ~ 0.001 Pa*s =1 cPoise
        if visc==None the solvent viscosity is calculated from
        function viscosity(solvent ,temp) with solvent eg 'h2o'

    Returns
    -------
    float
    diffusion coefficient in nm^2/ns

    """

    kT=Temp*kB
    if visc is None:
        visc=viscosity(solvent,Temp)*6.0221367e+23/1e9/1e9 # conversion from Pa*s= kg/m/s=u/nm/ns
    D0=kT/(6*math.pi*visc*Rh)*1000
    return D0

D0=Dtrans

def Drot(Rh,Temp=273.15,solvent='h2o',visc=None):
    """
    Rotational diffusion for a sphere.

    Parameters
    ----------
    Rh : float
        hydrodynamic radius in nm
    Temp : float
        temperature   in K
    solvent : float
        like in viscosity; used if visc==None
    visc : float
        viscosity in Pa*s  =>    H2O ~ 0.001 Pa*s =1 cPoise
        if visc==None the solvent viscosity is calculated from
        function viscosity(solvent ,temp) with solvent eg 'h2o'

    Returns
    -------
    float
    diffusion coefficient in 1/ns

    """

    kT=Temp*kB
    if visc is None:
        visc=viscosity(solvent,Temp)*6.0221367e+23/1e9/1e9 # conversion from Pa*s= kg/m/s=u/nm/ns
    D0=kT/(8*math.pi*visc*Rh**3)
    return D0

def molarity(objekt,c,total=None):
    """
    Calculates the molarity in mol/l (= mol/1000cm^3) if objekt is mass or has a .mass() method

    Parameters
    ----------
    objekt : object,float
        objekt with method .mass() or molecular weight in Da
    c : float
        concentration in g/ml -> mass/Volume
    total : float
        | total Volume in milliliter  [ml]
        | concentration is calculated by c[g]/total[ml]

    Returns
    -------
    float : molarity as mol/liter

    """
    if c>1:
        print( 'c limited to 1')
        c=1.
    if hasattr(objekt,'mass'):
        mass=objekt.mass()
    else:
        mass=objekt
    if total is not None:
        c=abs(float(c)/(float(total)))  # pro ml (cm^^3)  water density =1000g/liter
    if c>1:
        print( 'concentration c has to be smaller 1 unit is g/ml')
        return
    weightPerl=c*1000  # weight   per liter
    numberPerl=(weightPerl/(mass/constants.N_A))
    molarity=numberPerl/constants.N_A
    return molarity

def xyz2rphitheta(XYZ,transpose=False):
    """
    Transformation cartesian coordinates [X,Y,Z] to spherical coordinates [r,phi,theta].
    
    Parameters
    ----------
    XYZ : array 
        dim Nx3 with [x,y,z] coordinates ( XYZ.shape[1]==3 )
    transpose : bool
        Transpose XYZ before transformation.

    Returns
    -------
    array dim Nx3 with [r,phi,theta] coordinates
    phi   : float   azimuth     -pi < phi < pi
    theta : float   polar angle  0 < theta  < pi
    r     : float       length

    Examples
    --------
    Single coordinates
    ::

     js.formel.xyz2rphitheta([1,0,0])

    Transform Fibonacci lattice on sphere to xyz coordinates
    ::

     fib=js.formel.fibonacciLatticePointsOnSphere(10,1)
     js.formel.xyz2rphitheta(fib)

    Tranformation 2D X,Z coordinates in plane to r,phi coordinates (Z=0)
    ::

     rp=js.formel.xyz2rphitheta([data.X,data.Z,abs(data.X*0)],transpose=True) )[:,:2]

    """
    xyz=np.array(XYZ,ndmin=2)
    if transpose:
        xyz=xyz.T
    assert xyz.shape[1]==3 , 'XYZ second dimension should be 3. Transpose it?'
    rpt=np.zeros(xyz.shape)
    rpt[:,0]=(xyz**2).sum(axis=1)**0.5
    rpt[:,1]=np.arctan2(xyz[:,1],xyz[:,0])    # arctan2 is special function for this purpose
    rpt[:,2]=np.arctan2((xyz[:,:-1]**2).sum(axis=1)**0.5,xyz[:,2])
    return np.array(rpt.squeeze(),ndmin=np.ndim(XYZ))

def rphitheta2xyz(RPT,transpose=False):
    """
    Transformation  spherical coordinates [r,phi,theta]  to cartesian coordinates [x,y,z]
    
    Parameters
    ----------
    RPT : array 
        | dim Nx3 with [r,phi,theta] coordinates
        | r     : float       length
        | phi   : float   azimuth     -pi < phi < pi
        | theta : float   polar angle  0 < theta  < pi


    Returns
    -------
    array dim Nx3 with [x,y,z] coordinates
    
    """
    rpt=np.array(RPT,ndmin=2)
    if transpose:
        xyz=xyz.T
    assert rpt.shape[1]==3 , 'RPT second dimension should be 3. Transpose it?'
    xyz=np.zeros(rpt.shape)
    xyz[:,0]=rpt[:,0]*np.cos(rpt[:,1])*np.sin(rpt[:,2])
    xyz[:,1]=rpt[:,0]*np.sin(rpt[:,1])*np.sin(rpt[:,2])
    xyz[:,2]=rpt[:,0]*np.cos(rpt[:,2])
    return np.array(xyz.squeeze(),ndmin=np.ndim(RPT))

def T1overT2(tr=None,Drot=None,F0=20e6,T1=None,T2=None):
    r"""
    Calculates the T1/T2 from a given rotational correlation time tr or Drot for proton relaxation measurement

    tr=1/(6*D_rot)  with rotational diffusion D_rot and correlation time tr
    
    Parameters
    ----------
    tr : float
        rotational correlation time
    Drot : float
        if given tr is calculated from Drot
    F0 : float
        NMR frequency e.g. F0=20e6 Hz=> w0=F0*2*np.pi is for Bruker Minispec
        with B0=0.47 Tesla
    T1 : float
        NMR T1 result in s
    T2 : float
        NMR T2 resilt in s     to calc t12 directly

    Returns
    -------
    float : T1/T2

    Notes
    -----

    :math:`J(\omega)=\tau/(1+\omega^2\tau^2)`

    :math:`T1^{-1}=\frac{\sigma}{3} (2J(\omega_0)+8J(2\omega_0))`

    :math:`T2^{-1}=\frac{\sigma}{3} (3J(0)+ 5J(\omega_0)+2J(2\omega_0))`

    :math:`tr=T1/T2`

    References
    ----------
    .. [1] Intermolecular electrostatic interactions and Brownian tumbling in protein solutions.
           Krushelnitsky A
           Physical chemistry chemical physics 8, 2117-28 (2006)
    .. [2] The principle of nuclear magnetism A. Abragam Claredon Press, Oxford,1961


    """
    w0=F0*2*np.pi
    J=lambda w,tr:tr/(1+w**2*tr**2)
    if Drot is not None:
        # noinspection PyUnusedLocal
        tr=tr=1./(6*Drot)

    t1sig3=1./(2.*J(w0,tr)+8.*J(2*w0,tr))
    t2sig3=1./(3.*tr+5*J(w0,tr)+J(2*w0,tr))
    if T1 is not None:
        print( 'T1: %(T1).3g sigma = %(sigma).4g'%{'T1':T1,'sigma':t1sig3*3./T1})
    if T2 is not None:
        print( 'T2: %(T2).3g sigma = %(sigma).4g'%{'T2':T2,'sigma':t2sig3*3./T2})
    return t1sig3/t2sig3

def DrotfromT12(t12=None,Drot=None,F0=20e6,Tm=None,Ts=None,T1=None,T2=None):
    """
    Rotational correlation time from  T1/T2 or T1 and T2 from NMR proton relaxation measurement.

    Allows to rescale by temperature and viscosity.

    Parameters
    ----------
    t12 : float
        T1/T2 from NMR with unit seconds
    Drot : float
        !=None means output Drot instead of rotational correlation time
    F0 : float
        resonance frequency of NMR instrument
        for Hydrogen F0=20 MHz => w0=F0*2*np.pi
    Tm f: float
        temperature of measurement in K
    Ts :  float
        temperature needed for Drot   -> rescaled by visc(T)/T
    T1 : float
        NMR T1 result in s
    T2 : float  
        NMR T2 result in s     to calc t12 directly
        remeber if the sequence has a factor of 2
        
    Returns
    -------
        float    correlation time or Drot

    Notes
    -----
    See T1overT2

    """
    if T1 is not None and T2 is not None and t12 is None:
        t12=T1/T2
    if Tm is None:
        Tm=293
    if Ts is None:
        Ts=Tm
    if t12 is not None:
        diff=lambda tr,F0:T1overT2(tr=tr,Drot=None,F0=F0,T1=None,T2=None)-t12
        # find tr where diff is zero to invert the equation
        trr=scipy.optimize.brentq(diff,1e-10,1e-5,args=(F0,))
        # rescale with visc(T)/T
        tr=trr*(Tm/viscosity('d2o',T=Tm))/(Ts/viscosity('d2o',T=Ts))
        print( 'tau_rot: %(trr).3g at Tm=%(Tm).5g \ntau_rot: %(tr).5g at Ts=%(Ts).3g \n  (scalled by Tm/viscosity(Tm)/(T/viscosity(T)) = %(rv).4g'%{
            'trr':trr,'Tm':Tm,'tr':tr,'Ts':Ts,'rv':tr/trr})
    else:
        raise Exception('give t12 or T1 and T2')
    temp=T1overT2(trr,F0=F0,T1=T1,T2=T2)
    print('D_rot= : %(drot).4g '%{'drot':1/(6*tr)})
    if Drot is not None:
        Drot=1/(6*tr)
        print( 'returns Drot')
        return Drot
    return tr

def sedimentationProfileFaxen(t=1e3,rm=48,rb=85,number=100,rlist=None,c0=0.01,s=77,Dt=1.99e-11,w=246,
                              Rh=None,solvent='h2o',temp=293,densitydif=None):
    """
    Faxen solution to the Lamm equation of sedimenting particles in centrifuge; no bottom part

    bottom equillibrium distribution is not in Faxen solution included
    results in particle distribution along axis for time t

    Parameters
    ----------
    t : float
        Time after start in seconds.
    rm : float
        Axial position of meniscus in mm.
    rb : float
        Axial position of bottom in mm.
    number : integer
        Number of points between rm and rb to calculate.
    c0 : float
        Initial concentration in cell; just a scaling factor.
    s : float
        Sedimentation coefficient in Svedberg; 77 S is r=10 nm particle in H2O.
    Dt : float
        Translational diffusion coefficient in m**2/s; 1.99e-11 is r=10 nm particle.
    w : float
        Radial velocity rounds per second; 246 rps=2545 rad/s  is 20800g in centrifuge fresco 21.
    Rh : float
        Hydrodynamic radius in nm ; if given the Dt and s are calculated from this.
    solvent : {'h2o','d2o', 'toluol'}
        Solvent type for viscosity calculation.
    densitydif : float
        Density difference between solvent and particle in g/ml; protein in 'h2o'=> is used =>1.35-1.= 0.35 g/cm**3

    Returns
    -------
    dataArray with concentration distribution along r for timt t
    
    Notes
    -----
    .pelletfraction is the content in pellet as fraction already diffused out

    default values are for Heraeus Fresco 21 at 21000g

    References
    ----------
    .. [1] Über eine Differentialgleichung aus der physikalischen Chemie.
           Faxén, H. Ark. Mat. Astr. Fys. 21B:1-6 (1929)

    """
    # get solvent viscosity
    if solvent in ['h2o','d2o']:
        visc=viscosity(solvent,temp)
    if densitydif is None:
        densitydif=0.35 # protein - water
    densitydif*=1e3# to kg/m³
    timelist=dL()
    if Rh is not None:
        kT=temp*kB
        Dt=kT/(6*math.pi*visc*Rh*1e9)
        S=2./9./visc*densitydif*(Rh*1e-9)**2/1e-13
    svedberg=1e-13
    s*=svedberg
    rm/=1000.
    rb/=1000.# end
    r=np.r_[rm:rb:number*1j] # nn points
    if rlist is not None:
        rm=min(rlist)
        rb=max(rlist) # not used here
        r=rlist/1000.
    w=w*2*np.pi
    for tt in np.atleast_1d(t):
        ct=(0.5*c0*np.exp(-2.*s*w**2*tt))
        cr=(1-scipy.special.erf((rm*(w**2*s*tt+np.log(rm)-np.log(r)))/(2.*np.sqrt(Dt*tt))))
        timelist.append(dA(np.c_[r*1000,cr*ct].T))
        timelist[-1].time=tt
        timelist[-1].rmeniscus=rm
        timelist[-1].w=w
        timelist[-1].Dt=Dt
        timelist[-1].c0=c0
        timelist[-1].sedimentation=s/svedberg
        timelist[-1].pelletfraction=1-scipy.integrate.simps(y=timelist[-1].Y,x=timelist[-1].X)/(max(r)*1000*c0)
        timelist[-1].modelname=inspect.currentframe().f_code.co_name
        if Rh is not None: timelist[-1].Rh=Rh
    if len(timelist)==1:
        return timelist[0]
    return timelist

def sedimentationProfile(t=1e3,rm=48,rb=85,number=100,rlist=None,c0=0.01,S=None,Dt=None,omega=246,
                         Rh=10,solvent='h2o',temp=293,densitydif=0.41,solventvisc=None):
    """
    Approximate solution to the Lamm equation of sedimenting particles in centrifuge including bottom equilibrium distribution.

    Bottom equilibrium distribution is not in faxen solution.
    Results in particle concentration profile between rm and rb for time t

    Parameters
    ----------
    t : float
        time after start in seconds
    rm : float
        axial position of meniscus in mm
    rb : float
        axial position of bottom in mm
    number : int
        number of points between rm and rb to calculate
    rlist : list of float
        explicit list of positions where to calculate eg to zoom bottom
    c0 : float
        initial concentration in cell; just a scaling factor
    S : float
        sedimentation coefficient in Svedberg; 77 S is r=10 nm particle in H2O
    Dt : float
        translational diffusion coefficient in m**2/s; 1.99e-11 is r=10 nm particle
    omega : float
        radial velocity rounds per second; 246 rps=2545 rad/s  is 20800g in centrifuge fresco 21
    Rh : float
        hydrodynamic radius in nm ; if given the Dt and s are calculated from this.
    solvent : {'h2o','d2o'}
        solvent type for viscosity calculation
    densitydif : float
        density difference between solvent and particle in g/ml;
        protein in 'h2o'=> is used =>1.41-1.= 0.41 g/cm**3
    solventvisc : float, default None
        viscosity of the solvent if not h2o or d2o
        viscosity in Pa*s  =>    H2O ~ 0.001 Pa*s =1 cPoise

    Returns
    -------
        dataArray with [position[mm]; concentration; conc_meniscus_part; conc_bottom_part]

    Notes
    -----
    | "The deviations from the expected results are smaller than 1% for simulated curves and are valid for a
    | great range of molecular masses from 0.4 to at least 7000 kDa. The presented approximate solution,
    | an essential part of LAMM allows the estimation of s and D with an accuracy comparable
    | to that achieved using numerical solutions, e.g the program SEDFIT of Schuck et al."

    Default values are for Heraeus Fresco 21 at 21000g.

    References
    ----------
    .. [1] A new approximate whole boundary solution of the Lamm equation for the analysis of sedimentation velocity experiments
           J. Behlke, O. Ristau  Biophysical Chemistry 95 (2002) 59–68

    """
    # make here all in SI units
    if solvent in ['h2o','d2o']:
        # in Pa*s
        visc=viscosity(solvent,temp)
    else:
        if isinstance(solventvisc,(float,int)):
            visc=solventvisc
        else:
            raise Exception('If solvent is not in h2o, d2o the solvent viscosity needs to be given!')
    densitydif*=1e3   # to kg/m³
    if isinstance(t,(int,float)): t=np.r_[t]
    timelist=dL()
    if Rh is not None:
        kT=temp*kB
        Dt=kT/(6*math.pi*visc*Rh*1e9)
        S=2./9./visc*densitydif*(Rh*1e-9)**2/1e-13
    svedberg=1e-13
    S*=svedberg
    rm/=1000.# meniscus in m
    rb/=1000.# bottom in m
    r=np.r_[rm:rb:number*1j] # nn points in m
    if rlist is not None:  # explicit given list between meniscus and bottom
        r=rlist/1000.
    # create variables for calculation
    omega=omega*2*np.pi           # in rad
    taulist=2*S*omega**2*np.atleast_1d(t)           # timevariable for moving boundary
    # x=(r/rm)**2                  # not used
    # meniscus part
    eps=2*Dt/(S*omega**2*rm**2)
    w=2*(r/rm-1)
    b=1-0.5*eps
    # bottom part
    epsb=2*Dt/(S*omega**2*rb**2)
    d=1-epsb/2.
    z=2*(r/rb-1)
    # use scipy and numpy functions
    erfc=scipy.special.erfc
    erfcx = scipy.special.erfcx
    exp=np.exp
    sqrt=np.sqrt
    # moving meniscus part
    # one makes errors dependent on values , to resolve this i had to change as decribed
    # i have to test more examples to see if the c3 solution is needed also for c2
    c1=lambda tau:erfc((exp(tau/2.)-0.5*w-1+0.25*eps*(exp(-tau/2.)-exp(tau/2.)))/sqrt(eps*(exp(tau)-1)))
    c2=lambda tau:-(exp(b*w/eps)/(1-b))*erfc(  (w+2*b*(exp(tau/2.)-1))/(2*sqrt(2*eps*(exp(tau/2.)-1)))   )
    # c2 error:  exp(b*w/eps) goes infinity even if erfc is zero -> so exp of log to compensate before exp is taken
    #c2=lambda tau:-1./(1-b)*exp((b*w/eps)+np.log(erfc((w+2*b*(exp(tau/2.)-1))/(2*sqrt(2*eps*(exp(tau/2.)-1))))))
    # same here
    #c3=lambda tau:(2-b)/(1-b)*exp( (w+2*(exp(tau/2.)-1)*(1-b))/eps)*       erfc( (w+2*(exp(tau/2.)-1)*(2-b)) / (2*sqrt(2*eps*(exp(tau/2.)-1)))  )
    #c3=lambda tau:(2-b)/(1-b)*exp(((w+2*(exp(tau/2.)-1)*(1-b))/eps)+np.log(erfc( (w+2*(exp(tau/2.)-1)*(2-b)) / (2*sqrt(2*eps*(exp(tau/2.)-1))))))
    def c3(tau):
        # to avoid RuntimeWarning in  c3: divide by zero encountered in log for np.log(  erfc(xxerfc)
        # i use erfcx and take the additional exp(-xxerfc) in front of log
        xxerfc=(w + 2 * (exp(tau / 2.) - 1) * (2 - b)) / (2 * sqrt(2 * eps * (exp(tau / 2.) - 1)))
        res=(2 - b) / (1 - b) * exp( ((w + 2 * (exp(tau / 2.) - 1) * (1 - b)) / eps) + -xxerfc**2 + np.log(  erfcx(xxerfc)   ) )
        return res

    # bottom part
    cexptovercfax=lambda tau:c1(tau)+c2(tau)+c3(tau)
    c4=lambda tau:-erfc((d*tau-z)/(2*sqrt(epsb*tau)))
    c5=lambda tau:-exp(d*z/epsb)/(1-d)*erfc((-z-d*tau)/(2*sqrt(epsb*tau)))
    c6=lambda tau:(2-d)/(1-d)*exp(((1-d)*tau+z)/epsb)*erfc((-z-(2-d)*tau)/(2*sqrt(epsb*tau)))
    # add both
    cexptovercbottom=lambda tau:c4(tau)+c5(tau)+c6(tau)
    for tau in taulist:
        timelist.append(dA(np.c_[r*1000,(cexptovercfax(tau)+cexptovercbottom(tau))*c0/2./exp(tau)].T))
        timelist[-1].time=tau/(2*S*omega**2)
        timelist[-1].rmeniscus=rm
        timelist[-1].rbottom=rb
        timelist[-1].w=w
        timelist[-1].Dt=Dt
        timelist[-1].c0=c0
        timelist[-1].viscosity=visc
        timelist[-1].sedimentation=S/svedberg
        timelist[-1].modelname=inspect.currentframe().f_code.co_name
        # timelist[-1].pelletfraction=1-scipy.integrate.simps(y=timelist[-1].Y, x=timelist[-1].X)/(max(r)*1000*c0)
        if Rh is not None: timelist[-1].Rh=Rh
        timelist[-1].columnname='position[mm]; concentration; conc_meniscus_part; conc_bottom_part'

    if len(timelist)==1:
        timelist[0].setColumnIndex(iey=None)
        return timelist[0]
    timelist.setColumnIndex(iey=None)
    return timelist
