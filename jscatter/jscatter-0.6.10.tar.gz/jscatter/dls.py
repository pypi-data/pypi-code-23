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
Functions to read DLS data, apply the CONTIN analysis and plot the CONTIN results.

This is a wrapper around the original Fortran code of S. Provencher.
As the license is unclear please download and install if needed.

For CONTIN refer to  http://s-provencher.com/contin.shtml

**For using CONTIN and the wrapper you need a working CONTIN executable in your path.**
::

 # Download the FORTRAN source code from his webpage in a browser or
 wget http://s-provencher.com/pub/contin/contin.for.gz
 gunzip contin.for.gz
 # compile with gfortran
 gfortran contin.for -o contin
 # move to a place in your PATH eg $HOME/local/bin
 mv contin $HOME/local/bin/contin
 # check if it is executable, open a new shell
 which contin
 # if not found check if the path is in your PATH variable and set it in .bashrc or .profile
 # if still not found may be its not executable; so make it
 chmod u+x $HOME/local/bin/contin
 # reload the dls module
 reload(js.dls)


References

.. [1]  S.W. Provencher:
        Inverse problems in polymer characterization: Direct analysis of polydispersity with photon correlation spectroscopy.
        Makromol. Chem. 180, 201 (1979).
.. [2]  S.W. Provencher:
        A constrained regularization method for inverting data represented by linear algebraic or integral equations.
        Comput. Phys. Commun. 27, 213 (1982).
.. [3]  S.W. Provencher:
        CONTIN: A general purpose constrained regularization program for inverting noisy linear algebraic and integral equations.
        Comput. Phys. Commun. 27, 229 (1982).


---------------
"""
from __future__ import print_function
from __future__ import division

import io
import codecs
import collections
import locale
import numpy as np
import os
import sys
import time
from math import pi
from . import formel
from . import GracePlot
from .dataarray import dataArray as dA
from .dataarray import dataList as dL

# As CONTIN uses cgs units we use these here too

kb=1.3806505e-16 #cm2 g s-2 K-1

path = os.path.realpath(os.path.dirname(__file__))

import subprocess
#http://bugs.pythoorg/issue1731717
#this workaround at http://bugs.pythoorg/issue1236
# subprocess._cleanup = lambda: None
subprocess._cleanup = lambda: None

# find continexe
try:
    p = subprocess.Popen('which contin', shell=True,
                         bufsize=0,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    continexe=p.communicate()[0].strip()
except:
    continexe=''


def w2f(word):
    """converts if possible to float"""
    try:
        return float(word)
    except ValueError:
        return word

def _visc(T,**kw):
    # T in degrees
    # a viscosity calculation based on temperature
    # calc viscosity  in cPoise=1e3*[Pa*s]
    if 'v' in kw and kw['v'][0]=='d':
        v=1e3*formel.viscosity(mat='d2o',T=T)         # heavy water
    elif 'v' in kw and kw['v'][0]=='h':
        v=1e3* formel.viscosity(mat='h2o',T=T)
    elif 'v' in kw:
        v=kw['v']
    else:
        v=1e3*formel.viscosity(mat='h2o',T=T)        # default to normal water
    return v       #in cPoise

def contin(datalist,Ngrid=256,tmin=-2,tmax=-2,bgr=0,distribution='dls',RDG=-1,timescale=1e-6,**kw):
    """
    Inverse Laplace transform known as CONTIN analysis developed by Steven Provencher [1,2]_ .
    
    This is a wrapper for the original FORTRAN programm from Steven Provencher. 
    The CONTIN analysis is developed for heterodisperse, polydisperse, and multimodal systems that cannot
    be resolved with the cumulant method. The resolution for separating two different particle 
    populations is approximately a factor of five or higher and the difference in relative 
    intensities between two different populations should be less than 1:10−5. (from Wikipedia and own experience).
    Iuser[i] and Rxx are defined in the original Fortran code.

    Parameters
    ----------
    datalist : dataList or single dataArray
        Correlation data as measured e.g. by DLS
        Check type parameter dependent on input data g1 or g2!!!!
        Each dataArray is processed.
    timescale : float; default 1e-6
        Timescale factor. CONTIN uses internal units of seconds.
        As typical instruments use microseconds the time axis needs to be scaled by this factor.
    Ngrid : int
        Number of points between min and max.
    tmin,tmax : float,int
        First/last timevalue to use in fit
        If tmin/tmax are negative the number of points are droped at begin/end.
        eg min=-5 drops the 5 shortest timepoints; for max the 5 last points
    gmin/gmax : float
        First/last time value in distribution
        If not given calculated from tmin/tmax according to used kernel
    qgmin/qgmax : float
        Only for 'relax'.  Same as gmin,gmax except that gmin=qgmin/q^2
    qtmin/qtmax : float
        q^2*t scaled times
    bgr : float; default 0
        if >0:assume background and fit it
    typ :  int;  default 0
         |  0    input is g1 (Field correlation)
         |        -> means dont change input  in datalist
         |  1    input is intensity correlation g2 as measured by DLS;
         |        =>  field correlation is calculated as  g1= sign(g2/R21-1)*abs(g2/R21-1)^0.5
         | -1    input is g2-1 of DLS,  takes only the square root; sign preserved as for 1
         |                ALV and Malvern Zetasizer save g2-1
    distribution : string, default='x',
        | selects Iuser(10) as {'m':1,'D':2,'L':2,'r':3,'u':4,'x':4,'d':4,'T':4} according to first character of distribution
        | and RUSER(15,16,17,19). The kernel  g1=l^R23*exp(-R21*t*l^R22) describes always the field correlation
        | 'molweight'  weigth fraction molecular weight (mw) distribution l=mw -> mw*exp(-q**2*R18**t*mw**R22)
        | or 'mass'       R18 to be set in input: relates diffusion coefficient to mol weight
        |                 R22 to be set in input: exponent eg for polymers IN THETA solvent Diffusion=R18*l^0.5
        |                 R21 = R20**2*R18=q**2*R18
        |                 R23=1
        |                 l=mw and field(0)~ mw for weight fraction (intensity ~ mw**2)
        | 'Diff'       intensity weigth diffusion coefficient distribution with l=Diff -> exp(-q**2*t*Diff);
        |                 R23 =0
        |                 R22 =1
        |                 R21 =R20^2=q^2
        |                 l is therefore Diffusion coefficient
        | 'Laplace'    Laplace transform  with exp(-t*Gamma)
        |                 R23=0
        |                 R22=1
        |                 sets R16=0 (wavelength) => R20=undefined and R21=1
        |                 l is therefore relaxation rate with transform exp(-t*l)
        | 'radius'     weight fraction radius distribution of spheres satisfying stokes law
        |                 with l=rh -> rh**3*exp(-q**2* [k_B*T*/(0.06*pi*visc*rh)] * t)
        |                 R23=3
        |                 R22=-1
        |                 R21=k_B*R18*R20^2/(0.06pi*R19)
        |                 and l=rh is a the hydrodynamic radius
        |                 weight fraction as field(0) ~ V ~ rh**3 for spheres
        | 'x' or      intensity weight relaxation times distribution l=T -> exp(-t/T)
        |                 R21=1, R22=-1, R23=0
        | 'T1'        intensity weight relaxation times distribution l=T1 -> T1*exp(-t/T1)
        |                 for nmr rotational diffusion T1 with R23=-1 R21=1, R22=-1 neglecting T2
        |                 intensity ~ number of contributing atoms ~M ~ V ~ Rh**3
        |                 rot correlation time tc=(4pi*visc/kT)*Rh**3 -> intensity(0) ~ tc -> R23=1
        | 'dls'       intensity weight radius distribution of spheres satisfying stokes law
        |                 with l=rh -> exp(-q**2* [k_B*T*/(0.06*pi*visc*rh)] * t)
        |                 R21 = k_B*T*/(0.06*pi*visc)
        |                 R22=-1, R23=0
        | 'user'       general case RUSER(15,16,17,19,21,22,23) all user specified
        |                 eg R16=0,R23=0,R22=-1,R21=0 is laplace with Gamma^-1
    RDG :  1,-1, default = -1   
        | 1  use rayleighDebyeGans formfactor with wall thickness WALL [cm] of holow sphere (default WALL =0)
        | distribution needs to be the 'radius' distribution
    l : float , R16 overrides value in dataArray if given
        | overrides wavelength in data and set it to 632 nm
        | (except for Laplace and relaxation then l=0 overrides this because no wavelength is used)
    n : float, R15, overrides value in dataArray if given
        refractive index of solvent, default 1.333
    a : float, R17, overrides value in dataArray if given
        scattering angle in degrees , default 90°
    T : float, R18, overrides value in dataArray if given
        absolute Temperature in K or factor ; default is 293K
    WALL : float, R24, overrides value in dataArray if given
        | wall thickness  in cm for simulation of hollow spheres =0 normal sphere as default
        | if WALL<=0 will cause the hard sphere to be calculated wall =0
    v : float, R19, overrides value in dataArray if given
        | viscosity in centipoise; 1cPoise=1e-3 Pa*s
        | if v='d2o' or 'h2o' the viscosity of d2o or h2o at the given Temperature T is used
        | default is h2o at T
    write : any 
        if write is given as keyword argument (write=1) the contin output is writen to a file with the '.con' as ending

    Returns
    -------
        | input dataList with best solution added as parameters with name 'contin_'::
        |     .contin_bestFit               best fit result see below!!!!!!!!!!!!!!!!!
        |     .contin_result_fit            fitted correlation function
        |     .contin_fits                  sequence of fits in CONTIN same structure as best Fit
        |     .contin_alpha                 ALPHA of best solution
        |     .contin_alphalist             list of ALPHA in fits
        |     
        | dataArray with best solution distribution
        |     .contin_bestFit               [relaxation times,intensity weight ci, errors, hydrodynamic radii, mass weight ci , number weight ci]
        |     .contin_bestFit.attr()        shows all availible parameters from CONTIN fit and other parameters
        |     .contin_bestFit.fitquality    measure for the fitquality ALPHA and ...
        |     .contin_bestFit.peaks         original CONTIN results
        |                                   as intensity weight relaxation time distribution
        |     .contin_bestFit.ipeaks        data extracted from the peaks as list for all peaks in a solution
        |                                   it is a intensity weight relaxation time distribution
        |                                     [weight                 peak weight
        |                                       mean                  peak mean
        |                                       std                   peak standard deviation
        |                                       mean_err              error of mean
        |                                       imean                 index of peak mean
        |                                       1/(q**2*mean)         diffusion constant in cm**2/s
        |                                       Rh                    hydrodynamic radius in cm
        |                                       q                     wavevector in 1/cm
        |                                       1/(q**2*mean)         diffusion constant in nm**2/ns
        |                                       Rh                    hydrodynamic radius in nm
        |                                       q                     wavevector in 1/nm
        |                                       ]
        |     .contin_bestFit.mpeaks          same  for 2 strongest peaks mass  weight
        |     .contin_bestFit.npeaks          same  for 2 strongest peaks number weight
        |     .contin_bestFit.ipeaks_name'    content of ipeaks
        |     .contin_bestFit.info'
        |     .contin_bestFit.baseline'       baseline + error
        |     .contin_bestFit.momentEntireSolution'   all peaks together
        |     .contin_bestFit.maximum'        maximum value
        |     .contin_bestFit.filename'  
        |     .contin_bestFit.imaximum'       index maximum value
     
    Notes
    -----
    CONTIN  source and executable can be downloaded from http://s-provencher.com/pages/contin.shtml.

    Download and compile as (Linux and MacOS)
    ::

     wget http://s-provencher.com/pub/contin/contin.for.gz
     gunzip contin.for.gz
     gfortran contin.f -o contin
     # move to a place in your PATH that this module can find it

    If Peaks seem small please integrate them as the peak area determines the contributed intensity.
    Peak area is strongly dependent on the peak point separation P(i)*(x[i]-x[i-1]) in particular on a log scale.
    See [4]_ for details.
    ::

     ff=result.contin_bestFit
     p1=(10<ff.X) &(ff.X<100) # peak borders 10 and 100
     fp1=np.trapz(ff.Y[p1],ff.X[p1])/np.trapz(ff.Y,ff.X) # fraction of full signal

    **An example dataset with noise**
    Please test noise
    ::

     import jscatter as js
     import numpy as np
     t=js.loglist(1,100000,1000)   #times in microseconds
     q=4*np.pi/1.333/632*np.sin(np.pi/2) # 90 degrees for 632 nm , unit is 1/nm**2
     D=0.05*1000  # nm**2/ns * 1000 = units nm**2/microseconds
     noise=0.0001  # typical < 1e-3
     data=js.dA(np.c_[t,0.95*np.exp(-q**2*D*t)+noise*np.random.randn(len(t))].T)
     #Add attributes to overwrite defaults
     data.Angle      =90    # scattering angle in degrees
     data.Temperature=293   # Temperature of measurement  in K
     data.Viscosity  =1     # viscosity cPoise
     data.Refractive =1.333 # refractive index
     data.Wavelength =632   # wavelength
     p=js.grace()
     p.plot(data,legend='simulated data')
     p.xaxis(scale='l')
     # do CONTIN
     dr=js.dls.contin(data,distribution='x')
     js.dls.contin_display(dr)         # display overview
     # same but do it yourself
     p.plot(dr,li=1,sy=0,le='contin')
     p.plot(dr.contin_bestFit[0].X,dr.contin_bestFit[0].Y*100,sy=2)
     p.legend()
     # acces peak values by
     dr[0].contin_bestFit.ipeaks_name
     dr[0].contin_bestFit.ipeaks


    R20 (scattering vector) is calculated as R20= 4e-7*pi*R15/R16*sin(R17/2), if R16!=0. else R20=0



    References
    ----------
    .. [1] CONTIN: A general purpose constrained regularization program for inverting noisy linear algebraic and integral equations
           Provencher, S  Computer Physics Communications 27: 229.(1982)
           doi:10.1016/0010-4655(82)90174-6.
    .. [2] http://s-provencher.com/pub/contin/cpc2.pdf.
    .. [3] A constrained regularization method for inverting data represented by linear algebraic or integral equations
           Provencher, S. W. Comp. Phys. Commu 27: 213–227. (1982)
           doi:10.1016/0010-4655(82)90173-4
    .. [4] Transformation Properties of Probability Density Functions
           Stanislav Sýkora
           Permalink via DOI:  10.3247/SL1Math04.001

    Original code description in CONTIN
    ::

     C  THE FOLLOWING ARE THE NECESSARY INPUT -                                  0460
     C                                                                           0461
     C  DOUSIN = T (DOUSIN MUST ALWAYS BE .TRUE..)                               0462
     C                                                                           0463
     C  LUSER(3) = T, TO HAVE FORMF2, THE SQUARED FORM FACTORS, COMPUTED IN      0464
     C                USERK.                                                     0465
     C           = F, TO SET ALL THE FORMF2 TO 1. (AS WOULD BE APPROPRIATE       0466
     C                WITH LAPLACE TRANSFORMS).                                  0467
     C  RUSER(24) MAY BE NECESSARY INPUT TO SPECIFY THE FORM FACTOR (E.G.,       0468
     C            THE WALL THICKNESS OF A HOLLOW SPHERE) IF LUSER(3)=T.  SEE     0469
     C            COMMENTS IN USERK.                                             0470
     C  IUSER(18) MAY BE NECESSARY INPUT IF LUSER(3)=T (E.G., TO SPECIFY THE     0471
     C            NUMBER OF POINTS OVER WHICH THE SQUARED FORM FACTORS WILL      0472
     C            BE AVERAGED). SEE COMMENTS IN USERK.                           0473
     C                                                                           0474
     C  RUSER(16) = WAVELENGTH OF INCIDENT LIGHT (IN NANOMETERS),                0475
     C            = 0, IF RUSER(20), THE MAGNITUDE OF THE SCATTERING VECTOR      0476
     C                 (IN CM**-1), IS NOT TO BE COMPUTED.  WHEN                 0477
     C                 RUSER(16)=0, RUSER(15) AND RUSER(17) NEED NOT BE          0478
     C                 INPUT, AND CONTIN WILL SET RUSER(21)=1                    0479
     C                 (AS APPROPRIATE WITH LAPLACE TRANSFORMS).                 0480
     C                                                                           0481
     C  RUSER(15) = REFRACTIVE INDEX.                                            0482
     C  RUSER(17) = SCATTERING ANGLE (IN DEGREES).                               0483
     C                                                                           0484
     C                                                                           0485
     C  IUSER(10) SELECTS SPECIAL CASES OF USERK FOR MORE CONVENIENT USE.        0486
     C                                                                           0487
     C  IUSER(10) = 1, FOR MOLECULAR WEIGHT DISTRIBUTIONS FROM PCS               0488
     C                 (WHERE THE SOLUTION, S(G), IS SUCH THAT S(G)DG IS         0489
     C                 THE WEIGHT FRACTION WITH MOLECULAR WEIGHT BETWEEN         0490
     C                 G AND G+DG).                                              0491
     C                 CONTIN SETS -                                             0492
     C                   RUSER(23) = 1.,                                         0493
     C                   RUSER(21) = RUSER(18)*RUSER(20)**2.                     0494
     C                               (SEE ABOVE DISCUSSION OF RUSER(16).)        0495
     C                 YOU MUST INPUT -                                          0496
     C                   RUSER(18) TO SATISFY THE EQUATION (IN CGS UNITS) -      0497
     C                   (DIFFUSION COEFF.)=RUSER(18)*(MOL. WT.)**RUSER(22).     0498
     C                   RUSER(22) (MUST ALSO BE INPUT, TYPICALLY ABOUT -.5).    0499
     C                                                                           0500
     C  IUSER(10) = 2, FOR DIFFUSION-COEFFICIENT DISTRIBUTONS OR LAPLACE         0501
     C                 TRANSFORMS (WHERE G IS DIFF. COEFF. IN CM**2/SEC          0502
     C                 OR, E.G., TIME CONSTANT).                                 0503
     C                 CONTIN SETS -                                             0504
     C                   RUSER(23) = 0.,                                         0505
     C                   RUSER(22) = 1.,                                         0506
     C                   RUSER(21) = RUSER(20)**2 (SEE ABOVE DISCUSSION          0507
     C                                             OF RUSER(16).).               0508
     C                                                                           0509
     C  IUSER(10) = 3, FOR SPHERICAL-RADIUS DISTRIBUTIONS, ASSUMING THE          0510
     C                 EINSTEIN-STOKES RELATION (WHERE THE SOLUTION, S(G),       0511
     C                 IS SUCH THAT S(G)DG IS THE WEIGHT FRACTION OF             0512
     C                 PARTICLES WITH RADIUS (IN CM) BETWEEN G AND G+DG.         0513
     C                 WEIGHT-FRACTION DISTRIBUTIONS YIELD BETTER SCALED         0514
     C                 PROBLEMS THAN NUMBER-FRACTION DISTRIBUTIONS, WHICH        0515
     C                 WOULD REQUIRE RUSER(23)=6.)                               0516
     C                 CONTIN SETS -                                             0517
     C                   RUSER(23) = 3.,                                         0518
     C                   RUSER(22) = -1.,                                        0519
     C                   RUSER(21) = RUSER(20)**2*(BOLTZMANN CONST.)*            0520
     C                               RUSER(18)/(.06*PI*RUSER(19)).               0521
     C                               (SEE ABOVE DISCUSSION OF RUSER(16).)        0522
     C                 YOU MUST HAVE INPUT -                                     0523
     C                   RUSER(18) = TEMPERATURE (IN DEGREES KELVIN),            0524
     C                   RUSER(19) = VISCOSITY (IN CENTIPOISE).                  0525
     C                                                                           0526
     C  IUSER(10) = 4, FOR GENERAL CASE, WHERE YOU MUST HAVE INPUT -             0527
     C                 RUSER(J), J = 21, 22, 23.                                 0528
     C                                                                           0529
     C                                                                           0530



    """
    # contin is called in a shell like:  contin <input.txt >output.txt
    # we mimic this by subprocess.Popen
    # create a pipe to CONTIN with the input to stdin and stdout to outputpath = os.path.realpath(os.path.dirname(__file__))

    if continexe=='':
        raise Exception('There is no contin executable found. '+
                        'Please compile and place executable at callable path. '+
                        'See documentation of DLS module.')

    if datalist._isdataArray==True:
        datalist=dL(datalist)
    elif isinstance(datalist,str):
        datalist=dL(datalist)
    if len(datalist)==0:
        raise NameError('There are no data in datalist')

    # some consistency tests
    if 'typ' in kw:
        typ=kw['typ']
    else:typ=0
    if 'R22' in kw:
        if kw['R22']==0:
            raise ValueError('R22 is not allowed to be equal zero if given')

    # some defaults and functions #######################################################
    if  distribution[0]=='L':
        # set R16 =0 to get a real laplace l is otherwise the wavelength
        l=0
    elif 'l' in kw:l=kw['l']  # which is set with a default here
    else: l=632. #in nm
    if 'T' in kw:
        T=kw['T']
        del kw['T']
        if T< 273:
            print( 'Warning: temperature below ZERO!! ')
    elif 'R18' in kw:T=kw['R18']   # here we mis use the T as the proportianlity constant for kernel molweight
    else: T=293. # in K
    if 'n' in kw:n=kw['n']         # default refractive index
    else: n=1.333
    if 'a' in kw:a=kw['a']         # default angle
    else: a=90.                        # in degrees
    if bgr!=0 : bgr=1    # no background

    # wavevector in 1/cm
    qq= lambda n,ll,theta: 4.*pi*n/(ll*1e-7)*np.sin(np.deg2rad(theta)/2.)
    # hydrodynamic radius  Rh(relaxationtime) in cm, gamma is relaxation time visc in cPoise
    Rh=lambda gamma,q,T,visc:kb*T/(pi*0.06*visc)*q**2*gamma
    # mass_weight(t)
    massweight=lambda ci,qq,Ri:ci*Ri**3*qq**6/(np.sin(qq*Ri)-qq*Ri*np.cos(qq*Ri))**2
    # number weight
    numberweight=lambda ci,qq,Ri:ci*qq**6/(np.sin(qq*Ri)-qq*Ri*np.cos(qq*Ri))**2
    ##########################################################

    #DEFINES THE kind of the distribution kernel
    distr={ 'm':1,
            'D':2,'L':2,
            'r':3,
            'u':4,'x':4,'d':4,'T':4}
    if  distribution[0]=='m' and 'R18' not in kw.keys() and 'R21' not in kw.keys():
        print('please provide R18 and R22 in input to function')
        print("to describe D=R18*molWeight^R22    eg polymer R22=0.5")
        return
    if 'R22' in kw:
        R22=float(kw['R22'])
    else: R22=0
    if 'R21' in kw:
        R21=float(kw['R21'])
    else: R21=0
    if 'R23' in kw:
        R23=float(kw['R23'])
    else: R23=0
    edist=('x','T','d') # here we set R21-R23 explicitly in the later header part
    if distribution[0]=='x': #l^R23*exp(-R21*t*l^R22) with  R21=1,R22=-1,R23=0  ==> l=1/T -> exp(-t/T)
        R21=1
        R22=-1
        R23=0
    if distribution[0]=='T': # l^R23*exp(-R21*t*l^R22) with  R21=1,R22=-1,R23=1  ==> l=T -> T*exp(-t/T)
        R21=1
        R22=-1
        R23=1
    if distribution[0]=='d': # l^R23*exp(-R21*t*l^R22) with  R22=-1,R23=0  ==> l=Rh -> 1*exp(-R21*t/Rh)
        # I(t)=exp(- [  q**2*k_B*T*/(0.06*pi*visc)] * t/Rh )
        # l-> rh ; t=t ;  R21->  q**2* [k_B*T*/(0.06*pi*visc)]
        R21=kb*T/(0.06*pi*_visc(T,**kw)) * qq(n,l,a)**2       # D*Rh * Q**2
        R22=-1
        R23=0
    # write header für CONTIN als ASCII inputfile           #######################################
    last=1                  # for multi dataset evaluation this is -1 (false) except for the last one
                            # we process here ONLY single files
    elements=40             # just to have an array for it; last 2 lines are "end" and NY
    header=np.array(['']*elements,dtype='|S70') # a single fortran line
    header[0]='filename'.ljust(70)                                    # the loaded file
    header[1]='LAST'.ljust(6) +str().rjust(5)+('%15.4E' % last)       # see above
    #header[2]='GMNMX'.ljust(6)+str(1).rjust(5)+('%15.4E' % gmin)     # first point of the distribution to fit
    #header[3]='GMNMX'.ljust(6)+str(2).rjust(5)+('%15.4E' % gmax)     # last  point of the distribution to fit
    header[4]='IWT'.ljust(6)  +str().rjust(5) +('%15.4E' % 5)         # fit strategy how to determine errors -> 5 from a prefit, results in 2 fits but good errors
                                                                      # unweigthed fit IWT=1 ->errors equal; IWT=4 direct input of errors not implemented
    header[5]='NERFIT'.ljust(6)+str().rjust(5)+('%15.4E' % 0)         # number of points around a point to determine error; safty margin default 10; we use 0
    header[6]='NINTT'.ljust(6)+str().rjust(5)+('%15.4E' % -1)         # number of equally spaced sets in tk; <0 means direct input as used here
    header[7]='IFORMT'.ljust(6)+str().rjust(20)                       # format of time variable for direct input
    header[8]='(1E12.5)'.ljust(26)                                    # 1 in a row
    header[9]='IFORMY'.ljust(6)+str().rjust(20)                       # format of y variable for direct input correlation
    header[10]='(1E12.5)'.ljust(26)                                   # 1 in a row
    if 'IGRID' in kw.keys():header[11]=\
        'IGRID'.ljust(6)+str().rjust(5)+('%15.4E' % float(kw['IGRID'])) # Grid=2 is log grid ; 1 is equally spaced grid; default 2= log grid
    header[12]='NLINF'.ljust(6)+str().rjust(5)+('%15.4E' % bgr)       # allows a single const background , 0 no bgr
    header[13]='NG'.ljust(6)+str().rjust(5)+('%15.4E' % Ngrid)        # Ngrid  points between gmin,gmax
    header[14]='DOUSIN'.ljust(6)+str().rjust(5)+('%15.4E' % 1)        # Do User INPUT ; to use the below given values anyway this is the default
    header[15]='IUSER'.ljust(6)+str(10).rjust(5)+('%15.4E' % distr[distribution[0]])       # selects the kernel see help above
    header[16]='RUSER'.ljust(6)+str(15).rjust(5)+('%15.4E' % n)       # refractive index
    header[17]='RUSER'.ljust(6)+str(16).rjust(5)+('%15.4E' % l)       #  wavelength  in nm
    header[18]='RUSER'.ljust(6)+str(17).rjust(5)+('%15.4E' % a)       #  scattering angle in degrees
    header[19]='RUSER'.ljust(6)+str(18).rjust(5)+('%15.4E' % T)       # absolute Temperature in K or proportinality constant
    header[20]='RUSER'.ljust(6)+str(19).rjust(5)+('%15.4E' % _visc(T,**kw)) #viscosity in centipoise
    header[25]='RUSER'.ljust(6)+str(10).rjust(5)+('%15.4E' % typ)     # (0) means dont change; input is g1;
                                                                      # (1) input is intensity correlation g2; =>  calculate (g2/R21-1)^0.5
                                                                      # (-1) input is g2-1,  takes only the square root
                                                                      # ALV and Zetasizer Data are g2-1 -> -1
    header[26]='LUSER'.ljust(6)+str(3).rjust(5)+('%15.4E' % RDG)      # use rayleighDebyeGans formfactor (set to true => 1) or const 1 (set to false => -1 )
    if  'R16'   in kw.keys():header[17]='RUSER'.ljust(6)+str(16).rjust(5)+('%15.4E' % float(kw['R16']))
    if  'WALL'  in kw.keys():header[24]='RUSER'.ljust(6)+str(24).rjust(5)+('%15.4E' % float(kw['WALL']))  # wall thickness  in cm in RDG for simulationg of hollow spheres =0 normal sphere
    if 'ALPS1'  in kw.keys():header[27]='ALPST'.ljust(6)+str(1).rjust(5)+('%15.4E'  % float(kw['ALPS1'])) # take this alpha in preliminary error analysis
    if 'ALPS2'  in kw.keys():header[28]='ALPST'.ljust(6)+str(2).rjust(5)+('%15.4E'  % float(kw['ALPS2'])) # take this alpha in final analysis and as choosen solution
    if  'I18'   in kw.keys():header[29]='IUSER'.ljust(6)+str(18).rjust(5)+('%15.4E' % float(kw['I18']))   # formfactor average over 2 I18+1 points
    if  distribution[0] in edist or 'R21'   in kw.keys():header[22]='RUSER'.ljust(6)+str(21).rjust(5)+('%15.4E' % R21)
    if  distribution[0] in edist or 'R23'   in kw.keys():header[23]='RUSER'.ljust(6)+str(23).rjust(5)+('%15.4E' % R23)
    if  distribution[0] in edist or 'R22'   in kw.keys():header[21]='RUSER'.ljust(6)+str(22).rjust(5)+('%15.4E' % R22)
    if 'IQUAD'  in kw.keys():header[30]='IQUAD'.ljust(6)+str().rjust(5)+('%15.4E' % float(kw['IQUAD']))    # quadrature default=3 Simpson       1 is direct; 2 is trapezoidal
    if 'NORDER' in kw.keys():header[30]='NORDER'.ljust(6)+str().rjust(5)+('%15.4E' % float(kw['NORDER']))  # order regularization; default 2
    if 'PLEVEL' in kw.keys():
        word=('%5.2f' % float(kw['PLEVEL']))
        header[31]='PLEVEL'.ljust(6)
        header[32]=(word*4) # 0.1<PLEVEL<0.9  best is not to use it, default =0.5
    if 'NONNEG' in kw.keys():
        header[33]='NONNEG'.ljust(6)+str().rjust(5)+('%15.4E' %  float(kw['NONNEG'])) # no negative values in the solution default is 1;
    else:
        header[33]='NONNEG'.ljust(6)+str().rjust(5)+('%15.4E' % 1) ##   default is 1 as a distribution has no negative values
    header[-2]='END'.ljust(26)
    header[-1]='NY'.ljust(6)+str(0).rjust(5)         # Number of datapoints is set per file later
    #ende header für CONTIN als ASCII inputfile         ##################################

    # a default grid min max is needed if it is not given explicitly
    # to transform tmin and tmax  according to this function  from kernel exp   1=t*R21*l**R22  -> l=(t*R21)**-1/R22
    if  distribution[0]=='L':
        transk= lambda t,n,l,a,T,v,R22,R21:1/t
    elif distribution[0]=='m':
        transk= lambda t,n,l,a,T,v,R22,R21:(t*T*qq(n,l,a)**2)**(-1/R22)
    elif distribution[0]=='D':
        transk= lambda t,n,l,a,T,v,R22,R21:(t*qq(n,l,a)**2)**(-1)
    elif distribution[0]=='r':
        transk= lambda t,n,l,a,T,v,R22,R21:(t*kb*T*qq(n,l,a)**2/(0.06*pi*v))
    elif distribution[0]=='d':
        transk= lambda t,n,l,a,T,v,R22,R21:(t*kb*T*qq(n,l,a)**2/(0.06*pi*v))
    elif distribution[0]=='u' or distribution[0]=='x':
        transk= lambda t,n,l,a,T,v,R22,R21:(t*R21)**(-1/R22)
    elif distribution[0]=='T':
        transk= lambda t,n,l,a,T,v,R22,R21:(t*R21)**(-1/R22)

    ###################################
    # now look at the data
    idata=0
    print('processing  %i datasets ' %len(datalist))
    for data in datalist:
        idata+=1
        print(idata)
        try:
            file=getattr(data,'@name')[0]
        except AttributeError:
            file=time.strftime("%y%m%d%H%M%S", time.localtime())
        header[0]=file
        data.extract_comm(deletechars=':[]()"')              # find extra parameters in comments
        #data[0]*=0.001                                       # have all in s not in ms from ALV
        # extract datetime from comments from ALV instrument
        timestr=''
        for line in data.comment:
            if line[:4]=='Time' or line[:4]=='Date':
                try:
                    timestr+=line.translate(None,'"').split()[2]
                    datetime=time.mktime(time.strptime(timestr, "%d.%m.%Y%H:%M:%S"))
                except:
                    pass
        try:
            data.datetime=datetime
        except:
            data.datetime=0
        # take values from data
        # this allows to have float or list of float (take first)
        _getfirst = lambda a:a if isinstance(data.Angle,(float,int)) else a[0]
        if 'n' not in kw:
            try:
                n=_getfirst(data.Refractive)
            except:
                pass
        if 'l' not in kw and distribution[0]!='L' and 'R16' not in kw:
            try:
                l=_getfirst(data.Wavelength)
            except:
                pass
        if 'a' not in kw:
            try:
                a=_getfirst(data.Angle)
            except:
                pass
        if 'T' not in kw:
            try:
                T=_getfirst(data.Temperature)
            except:
                pass
        if 'v' not in kw:
            try:
                v=_getfirst(data.Viscosity)
            except:
                v=_visc(T,**kw)
        else:
            v=_visc(T,**kw)

        # or override it
        if l!=0:
            contin_wavevector=qq(n,l,a)         # in 1/cm
        else:
            contin_wavevector=0
        # create header for contin with parameters from datafile
        try:
            if 'qtmin' in kw: tmin=float(kw['qtmin'])/contin_wavevector**2
            if 'qtmax' in kw: tmax=float(kw['qtmax'])/contin_wavevector**2
        except AttributeError:
            raise('dont use qtmin / qtmax with Laplace option. wavevector is zero')
        itmin,itmax=data.X.searchsorted((tmin,tmax))         # searches where tmin,tmax fit into list and outputs the place
        if tmin<0: itmin=-tmin                                # if negative purge first points
        if tmax<0: itmax=tmax                                 # same but if negative count from behind
        try:
            if not 'gmin' in kw and not 'qgmin' in kw:
                gmin=transk(data.X[itmin],n,l,a,T,_visc(T,**kw),R22,R21)      # calculate min max of the grid if not given
            elif 'qgmin' in kw:
                gmin=float(kw['qgmin'])/contin_wavevector**2
            else: gmin=float(kw['gmin'])
            if 'gmax' not in kw and 'qgmax' not in kw:
                gmax=transk(data.X[itmax],n,l,a,T,_visc(T,**kw),R22,R21)
            elif 'qgmax' in kw:
                gmax=float(kw['qgmax'])/contin_wavevector**2
            else: gmax=float(kw['gmax'])
        except ZeroDivisionError:
            print('wavevector is zero; use qgmax/qgmin only with non laplace option')
        header[2]='GMNMX'.ljust(6)+str(1).rjust(5)+('%15.4E' % min(gmin,gmax))       # fit interval min
        header[3]='GMNMX'.ljust(6)+str(2).rjust(5)+('%15.4E' % max(gmin,gmax))       # fit interval max
        if 'T' not in kw and 'R18' not in kw:
            try:
                T=data.Temperature[0]
            except:
                T=273.15+20
            header[19]='RUSER'.ljust(6)+str(18).rjust(5)+('%15.4E' % T)
        header[16]='RUSER'.ljust(6)+str(15).rjust(5)+('%15.4E' % n)
        header[17]='RUSER'.ljust(6)+str(16).rjust(5)+('%15.4E' % l)
        header[18]='RUSER'.ljust(6)+str(17).rjust(5)+('%15.4E' % a)
        header[20]='RUSER'.ljust(6)+str(19).rjust(5)+('%15.4E' % v)

        p = subprocess.Popen(continexe, shell=True,
                                        bufsize=0,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

        # set the number of values
        lenX=len(data.X[itmin:itmax])
        header[-1]='NY'.ljust(6)+str(lenX).rjust(5)
        # now write the header and the data to a input buffer
        input=io.BytesIO()
        input.writelines([b' '+line+b'\n' for line in filter(lambda line:line!=b'',header)])
        input.writelines([b' '+(b'%8.5E' % line)+b'\n' for line in data.X[itmin:itmax]])
        if 'test' in kw:  #just as a test with simple exponential relax=valuefloat(kw['test'])
            input.writelines([' '+('%8.5E' % line)+'\n' for line in 1e-3+np.exp(-data.X[itmin:itmax]/float(kw['test'])*2)])
        else:
            input.writelines([b' '+(b'%8.5E' % line)+b'\n' for line in data.Y[itmin:itmax]])
        # to check input
        if 'write' in kw or 'w' in kw:
            with open('./'+'input.con','w') as f:zeilen=f.writelines(input.getvalue().decode('utf-8'))

        # now run contin in a shell like environment with pipes
        # with input in stdin and collect the stout and errot in output and error
        (output,error)=p.communicate(input.getvalue())
        output=output.decode('utf-8')
        error=error.decode('utf-8')
        input.close()
        if error!='':
            print(file,'      :',error)
        if len(output)==0:
            print('there was nothing in output yet')
            return
        #to check output
        if 'write' in kw or 'w' in kw:
            with open('./'+file+'.con','w') as f:zeilen=f.writelines(output)

        #### CONTIN finished and we look at the output##################

        # sort the output to the data
        outblocks=output.split('UNREGULARIZED VARIABLES')[-1].split(file)
        if len(outblocks)<3:
            print('last lines of CONTIN output')
            print(outblocks[-1])
            raise Exception('CONTIN ended with no result; use w=1 to get output for analysis')
        # blocks of different alpha in result (without prefit results);
        # first repeat input ; then preliminary res; last two choosen solution
        # second last is fit  ; last is result distribution

        # take the fit block after Abscissa;splitlines and take only lenX;split line to words and convert to float
        temp=np.r_[[[float(vv) for vv in line[:22].split()] for line in outblocks[-2].split('ABSCISSA\n')[-1].splitlines()[:lenX]]].T
        data.contin_result_fit=temp[[1,0]]          # resort to have xtime in 0 and fit_y in 1
        data.contin_fits=[]
        for k in range(len(outblocks))[1:-2]: #all solutions with different alpha
            chosen=outblocks[k].splitlines()

            # take the chosen block line 6 to 6+Ngrid;split into words and convert to float;   sometimes D is used instead of E for float 1E5
            # order of temp -> [y, error_y, t]
            temp=np.r_[[[float(vv) for vv in line[:31].replace('D','E').split()] for line in chosen[6:Ngrid+6]]].T
            ## fit quality in 3rd line of chosen last chosen block
            try:
                RR=Rh(temp[2]*timescale,contin_wavevector,T,v)            # hydrodynamic radius temp[2] is correlation time]
                ci_massw=massweight(temp[0],contin_wavevector,RR)         # mass weighted contribution ci  temp[0] is fraction
                ci_numw =numberweight(temp[0],contin_wavevector,RR)       # number weighted contribution
                #tohave [t,y,erronp.r_y] and hydrodyn Radius,  mass weight and number weightin the result output
                data.contin_fits.append(dA(np.c_[temp[[2,0,1]].T,RR,ci_massw,ci_numw].T))
            except:
                data.contin_fits.append(dA(np.c_[temp[[2,0,1]].T].T))

            # fitquality from contin output
            data.contin_fits[-1].fitquality={}
            name=[aa.lstrip() for aa in chosen[2].lstrip().split('    ')]
            line=chosen[3].split()
            if line[0]=='*':
                value=[float(li) for li in line[1:]]
            else:
                value=[float(li) for li in line[:]]
            for i in range(len(name)):
                data.contin_fits[-1].fitquality[name[i]]=value[i]
            # look at the peaks found at the end of solution block
            lines=chosen[Ngrid+6:]
            linesl=[]
            data.contin_fits[-1].peaks=[]
            entireSol=-1
            for i in range(len(lines)):
                if lines[i][:5]=='0PEAK':linesl.append(i)       #first peak line number
                if lines[i].strip()[:7]=='MOMENTS':entireSol=i  # entire solution line number
            # append if entire solution exists (does not for single peaks)
            if entireSol!=-1:
                data.contin_fits[-1].momentEntireSolution={}
                for j in 1,2,3,4,5:
                    val=lines[entireSol+j][44:].replace('X (10**','').replace(')','').split()
                    data.contin_fits[-1].momentEntireSolution['mom_'+val[0]]=[w2f(vv) for vv in [val[0],val[1]+'E'+val[2]]+val[3:-1]]
                data.contin_fits[-1].momentEntireSolution['std/mean']=w2f(lines[entireSol+4][:45].split()[-1])
            data.contin_fits[-1].baseline=[w2f(vv) for vv in np.r_[lines[0][22:].replace('D','E').split()][[0,2]]]
            for i in linesl:
                data.contin_fits[-1].peaks.append({})        # append a new peak
                words=lines[i].split()
                data.contin_fits[-1].peaks[-1]['nr']=w2f(words[1])
                data.contin_fits[-1].peaks[-1]['minmax']=[w2f(words[4]),w2f(words[6])]
                data.contin_fits[-1].peaks[-1]['iminmax']=[abs(data.contin_fits[-1][0]-data.contin_fits[-1].peaks[-1]['minmax'][0]).argmin(),
                                                           abs(data.contin_fits[-1][0]-data.contin_fits[-1].peaks[-1]['minmax'][1]).argmin()]
                for j in 1,2,3,4,5:
                    val=lines[i+j][44:].replace('X (10**','').replace(')','').split()
                    data.contin_fits[-1].peaks[-1]['mom_'+val[0]]=[w2f(vv) for vv in [val[0],val[1]+'E'+val[2]]+val[3:-1]]
                data.contin_fits[-1].peaks[-1]['std/mean']=w2f(lines[i+4][:45].split()[-1])
                data.contin_fits[-1].peaks[-1]['weight']=data.contin_fits[-1].peaks[-1]['mom_0'][1]
                data.contin_fits[-1].peaks[-1]['mean']=data.contin_fits[-1].peaks[-1]['mom_1'][3]
                data.contin_fits[-1].peaks[-1]['imean']=data.contin_fits[-1][0].searchsorted(data.contin_fits[-1].peaks[-1]['mean'])
                data.contin_fits[-1].peaks[-1]['mean_errproz']=data.contin_fits[-1].peaks[-1]['mom_1'][4]
                data.contin_fits[-1].peaks[-1]['mean_err']=data.contin_fits[-1].peaks[-1]['mom_1'][4]/100.*data.contin_fits[-1].peaks[-1]['mom_1'][3]
                # standard deviation is std=sqrt(mom2/mom1- mean**2)
                data.contin_fits[-1].peaks[-1]['std']=abs(data.contin_fits[-1].peaks[-1]['mom_2'][1]/data.contin_fits[-1].peaks[-1]['mom_0'][1]-data.contin_fits[-1].peaks[-1]['mom_1'][3]**2)**0.5
                data.contin_fits[-1].peaks[-1]['mean_num']=data.contin_fits[-1].peaks[-1]['mom_0'][3]
                if  distribution[0]=='m':  # mass fraction mol weigth see provencher
                    data.contin_fits[-1].peaks[-1]['mean_mass']=data.contin_fits[-1].peaks[-1]['mom_1'][3]
                    data.contin_fits[-1].peaks[-1]['mean_z']=data.contin_fits[-1].peaks[-1]['mom_1'][3]
                    data.contin_fits[-1].peaks[-1]['mean_z+1']=data.contin_fits[-1].peaks[-1]['mom_1'][3]
        # now the chosen solution from CONTIN, which is the last given (repeated)
        chosen=outblocks[-1].splitlines()
        data.contin_alpha=float(chosen[3].split()[0])  # this is the choosen solution alpha
        data.contin_alphalist=[f.fitquality['ALPHA'] for f in data.contin_fits]#
        data.contin_bestFit=data.contin_fits[data.contin_alphalist.index(data.contin_alpha)]              # this is the choosen solution
        data.contin_bestFit.imaximum=data.contin_bestFit[0].searchsorted(data.contin_bestFit[1].max())
        data.contin_bestFit.columnname='relaxationtimes;intensityweightci; errors; hydrodynamicradii; massweightci;numberweightci'
        # a short info about the peaks
        if 1:#try:
            ipeaks=np.c_[[[p['weight'],
                    p['mean'],
                    p['std'],
                    p['mean_err'],
                    p['imean'],
                    (1/(contin_wavevector**2*p['mean']*timescale) if contin_wavevector!=0 else 0),
                    Rh(p['mean']*timescale,contin_wavevector,T,v),
                    contin_wavevector,
                    (1e5/(contin_wavevector**2*p['mean']*timescale) if contin_wavevector!=0 else 0),
                    Rh(p['mean']*timescale,contin_wavevector,T,v)*1e7,
                    contin_wavevector*1e-7  ]
                    for p in data.contin_bestFit.peaks]]
            # sort for largest weigth  but take only npeak strongest
            sequence=ipeaks[:,0].argsort()[::-1]#[:3]
            ipeaks=ipeaks[sequence,:]
            # and sort the remaining  for peak position in wavevector contin_wavevector
            sequence=ipeaks[:,5].argsort()
            data.contin_bestFit.ipeaks=ipeaks[sequence,:]
            data.contin_bestFit.ipeaks_name=['weight',
                                    'mean',
                                    'std',
                                    'mean_err',
                                    'imean',
                                    'mean_Deff',
                                    'Rh',
                                    'wavevector',
                                    'mean_Deff_nmns',
                                    'Rh_nm',
                                    'wavevector_nm',
                                    ]
        else:#except:
            ipeaks=np.c_[[[p['weight'],
                    p['mean'],
                    p['std'],
                    p['mean_err'],
                    p['imean']]
                    for p in data.contin_bestFit.peaks]]
             # sort for largest weigth  but take only npeak strongest
            sequence=ipeaks[:,0].argsort()[::-1][:3]
            ipeaks=ipeaks[sequence,:]
            data.contin_bestFit.ipeaks=ipeaks
            data.contin_bestFit.ipeaks_name=['weight',
                                    'mean',
                                    'std',
                                    'mean_err',
                                    'imean']
        try:
        # calculate the mass weight properties
            temp=[]
            for p in data.contin_bestFit.peaks:
                imin=max(0,p['iminmax'][0]-1)
                imax=min(len(data.contin_bestFit[0]),p['iminmax'][1]+1)
                weight=np.trapz(data.contin_bestFit[4,imin:imax],data.contin_bestFit[0,imin:imax])
                mmean=np.trapz(data.contin_bestFit[4,imin:imax]*data.contin_bestFit[0,imin:imax],data.contin_bestFit[0,imin:imax])/weight
                std  =np.sqrt(np.trapz((data.contin_bestFit[4,imin:imax]*data.contin_bestFit[0,imin:imax]**2),data.contin_bestFit[0,imin:imax])/weight-mmean**2)
                temp.append([weight,
                              mmean,
                              std,
                              p['mean_err'],
                              min(data.contin_bestFit[0].searchsorted(mmean),len(data.contin_bestFit[0])),
                              (1/(contin_wavevector**2*mmean*timescale) if contin_wavevector!=0 else 0),
                              Rh(mmean*timescale,contin_wavevector,T,v),
                              contin_wavevector,
                              (1e5/(contin_wavevector**2*mmean*timescale) if contin_wavevector!=0 else 0),
                              Rh(mmean*timescale,contin_wavevector,T,v)*1e7,
                              contin_wavevector*1e-7])
            mpeaks=np.c_[temp]
            mpeaks[:,0]=mpeaks[:,0]/mpeaks[:,0].sum()
            mpeaks=mpeaks[sequence,:]
            data.contin_bestFit.mpeaks=mpeaks
            # calculate the number weight properties
            temp=[]
            for p in data.contin_bestFit.peaks:
                imin=max(0,p['iminmax'][0]-1)
                imax=min(len(data.contin_bestFit[0]),p['iminmax'][1]+1)
                weight=np.trapz(data.contin_bestFit[5,imin:imax],data.contin_bestFit[0,imin:imax])
                nmean=np.trapz(data.contin_bestFit[5,imin:imax]*data.contin_bestFit[0,imin:imax],data.contin_bestFit[0,imin:imax])/weight
                std  =np.sqrt(np.trapz((data.contin_bestFit[5,imin:imax]*data.contin_bestFit[0,imin:imax]**2),data.contin_bestFit[0,imin:imax])/weight-nmean**2)
                temp.append([weight,
                              nmean,
                              std,
                              p['mean_err'],
                              min(data.contin_bestFit[0].searchsorted(nmean),len(data.contin_bestFit[0])),
                              (1/(contin_wavevector**2*nmean*timescale)  if contin_wavevector!=0 else 0)  ,
                              Rh(nmean*timescale,contin_wavevector,T,v),
                              contin_wavevector,
                              (1e5/(contin_wavevector**2*nmean*timescale) if contin_wavevector!=0 else 0),
                              Rh(nmean*timescale,contin_wavevector,T,v)*1e7,
                              contin_wavevector*1e-7])
            npeaks=np.c_[temp]
            npeaks[:,0]=npeaks[:,0]/npeaks[:,0].sum()
            npeaks=npeaks[sequence,:]
            data.contin_bestFit.npeaks=npeaks
        except:
            pass
    return datalist

def contin_display(result_list,select=[],npeak=2,*args,**kw):
    """
     A routine to plot CONTIN results to get an overview over CONTIN output.
     
     Parameters
     ----------
     result_list : dataList
         Output of dls.contin.
     select : list of int  
         Sequence of integers in result_list to select for output.
     npeak : int 
         Number of peaks in output  default 2.
     dlogy :
         shows distribution in y logscale


    Notes
    -----
    | access diffusion of all first peaks by output[:,1,6]
    | mean and std as
    | output[:,1,6].mean()
    | output[:,1,6].std()

    """
    p=GracePlot()
    p.multi(1,3)
    p1=p.g[0]
    p1.subtitle('correlation')
    p2=p.g[1]        
    if 'mass' in kw.keys():
        p2title='mass weighted \\ndistribution'
    elif 'number' in kw.keys():
        p2title='number weighted \\ndistribution'
    else: #intensity
        p2title='intensity weighted \\ndistribution'
    p2.subtitle(p2title)
    p3=p.g[2]
    p3.subtitle('relaxation times')
    if isinstance(select,int):
        select=[select]
    if select==[]:
        select=range(len(result_list))
    for i in select:
        data=result_list[i]
        p1.plot(data[0],data[1],line=0,symbol=-1)
        p1.plot(data.contin_result_fit[0],data.contin_result_fit[1],line=-1,symbol=0)
        p1.yaxis(min=0.0001,scale='n')
        p1.xaxis(min=0.0001,scale='l')
        p1.ylabel('g1(t)')
        p1.xlabel(r't')
        if 'mass' in args:
            YY=data.contin_bestFit[4]/data.contin_bestFit[4].max()
            peaks=data.contin_bestFit.mpeaks
        elif 'number' in args:
            YY=data.contin_bestFit[5]/data.contin_bestFit[5].max()
            peaks=data.contin_bestFit.npeaks
        else: #intensity
            YY=data.contin_bestFit[1]/data.contin_bestFit[1].max()
            peaks=data.contin_bestFit.ipeaks
        if 'dlogy' in args:
            p2.plot(data.contin_bestFit[0],YY,
                    legend='%.3g a=%.3g PROB1 %.3g' %(data.contin_alpha,
                                                      data.contin_bestFit.fitquality['ALPHA'],
                                                      data.contin_bestFit.fitquality['PROB1 TO REJECT']),
                    symbol=-1)
            p2.xaxis(min=0.0001,scale='l')
            p2.yaxis(min=0.0001,scale='l')
        else:
            #try:
            p2.plot(data.contin_bestFit[0],YY,
                    legend='%.3g a=%.3g PROB1 %.3g' %(data.contin_alpha,
                                                      data.contin_bestFit.fitquality['ALPHA'],
                                                      data.contin_bestFit.fitquality['PROB1 TO REJECT']),
                    symbol=-1)
            p2.xaxis(min=0.0001,scale='l')
            #except: pass
        p2.ylabel('distr(t)')
        p2.xlabel(r't')
        p3.ylabel(r'peak\smean\N ')
        p3.xlabel(r'q / nm\S-1')

        for pp in peaks[:npeak]:
            p3.plot([pp[10]],[pp[1]],[pp[3]/pp[1]],symbol=-1,line=0)

    return

_mode='r'
if (sys.version_info < (3, 0)):
    # older version uses universal newline as 'U', from python 3 it is supported by default in 'r' mode
    _mode+='U'

def readZetasizerNano(filename,NANOcoding="cp1257",NANOlocale=['en_US','UTF-8']):
    """
    Read ascii file data exported from Malvern Zetasizer Nano.

    Format of Zetasizer is one measurement per line with content defined in export makro.
    First line gives names of columns as header line, so header line in NANO export is necessary.
    Lists as Sizes, Volumes... need to be separated by "sample name" because of different length.

    Parameters
    ----------
    filename : string
        Zetasizer filename
    NANOcoding : string
        UTF coding from Windows
    NANOlocale : list of string
        | encoding of weekday names in NAno textfile
        | ['de_DE','UTF-8'] NANO set to German
        | ['en_US','UTF-8'] NANO set to US
        | ...

    Returns
    -------
    dataList
        X,Y columns are
         * correlation data [CorrelationDelayTimes,sign(CorrData)*|CorrelationData|**0.5, CorrelationData] if present
         * or RelaxationTimes, Sizes, Intensities, Volumes, Diffusions if present
        If no correlation or sizes the data are zero and only parameters are stored.
        No unit conversion is done.
        Parameters contain any other information stored in line.

    CorrelationData.Y contains 1-g2=g1**2 with 0 for negative 1-g2.

    Notes
    -----
    The template for export in Zetasizer has some requirements:

    - The headerline should be included.
    - Separator is the tab.
    - First entries should be "Serial Number" "Type" "Sample Name" "Measurement Date and Time"
    - Sequence data as "Sizes", "Intensities" should be separated by "Sample Name" as separator.
    - Appending to same file is allowed if new headerline is included.

    Examples
    --------
    ::

    import jscatter as js
    import numpy as np
    import glob
    files=glob.glob('../rawdata/PC4EG4/pc4eg4*.txt')
    for file in files:
        data=js.dls.readZetasizerNano(file)
        p=js.grace()
        p.plot(data) # plots correlation function

    """
    seqcolumnNames=['CorrelationDelayTimes','CorrelationData',
                    'RelaxationTimes','Sizes','Intensities','Volumes','Diffusions',
                    'DistributionFitDelayTimes','DistributionFitData','DistributionFit']
    # DSL data are writen on windows computer with specific encoding
    #read it
    #locale.resetlocale()
    #get locale
    old_loc = locale.getlocale(locale.LC_TIME)
    #set it to german or english us dependent on DLS Computer language
    locale.setlocale(locale.LC_TIME, NANOlocale)
    #
    with codecs.open(filename,_mode,NANOcoding) as f:zeilen=f.readlines()

    output=dL()
    #scan each line
    for izeile,zeile in enumerate(zeilen):
        #encode in utf8 for correct use in datatime and split line
        worte=zeile.rstrip().replace(',','.').split('\t')
        para={}   # single parameters
        data={}   #sequence of data
        next=0
        # detect a headerline
        if any(x in worte[:4] for x in ['Serial Number','Record', 'Type', 'Sample Name']) :
            headerline=worte
            header=collections.OrderedDict()     #the key order is preserved in OrderedDict
            for i,field in enumerate(headerline):
                # if multiple entries as sequence it can be identified by '['
                key=field.split('[')[0].split('(')[0]
                if key not in header.keys():
                    header[''.join(key.split())]=[(i,field,key)]
                else:
                    header[''.join(key.split())]+=[(i,field,key)]
            continue
        if 'Trend'             in worte[:4]:continue        # skip Trend lines
        if 'Aggregation Point' in worte[:4]: continue       # skip line
        for key in header.keys():
            if '[' in header[key][0][1]\
                or key in seqcolumnNames  :                # belongs to a sequence of data as distribution fit
                start=next
                try:
                    #try to find index of next "SampleName" as separator
                    next=worte.index(para['SampleName'][0],start)
                except (ValueError,KeyError):
                    print('in line ',izeile,'',key,' is missing a "sample Name" after the sequence. Check your export template')
                    continue
                data[''.join(key.split())]=worte[start:next]
                next=next+1
            else:
                try:
                    #not a sequence; is only a parameter
                    if ''.join(key.split()) in para.keys(): # already there
                        para[''.join(key.split())]+=worte[next]
                    else:                                   # new one
                        para[''.join(key.split())]=[worte[next]]
                except:
                    print('in line ', izeile, '', key,
                          ' is missing parameter value. Check your export template')
                    continue
                next=next+1
        if data == {}:
            print('in line ', izeile, ' is missing data at all. Check your export template')
            continue
        #append to output as new dataArray
        names=[r'RelaxationTimes',r'Sizes',r'Intensities',r'Numbers',r'Volumes',r'Diffusions']
        columnnames=list(set(names).intersection(set(data.keys())))
        columnnames=[name  for name in names if name in columnnames]
        if 'CorrelationDelayTimes' in data.keys() and len(data['CorrelationData'])>0 :
            # we save here g1 instead of 1-g2 => take root later to prevent negative roots
            cor=np.array(data['CorrelationData'],dtype=float)
            output.append(dA(np.c_[np.array(data['CorrelationDelayTimes'],dtype=float),
                                   np.sign(cor)*np.sqrt(np.abs(cor)),cor].T,
                                   XYeYeX=[0,1]))
            del data['CorrelationDelayTimes']
            del data['CorrelationData']
            output[-1].columnname='CorrelationDelayTimes; CorrelationData=g2-1'
        elif len(columnnames)>0:
            output.append(dA(np.c_[[np.array(data[name],dtype=float) for name in  columnnames]],XYeYeX=[0,1]))
            output[-1].columnname=''.join(['%s; ' %(name) for name in  columnnames])
            for coln in names[2:]:
                if coln in columnnames:
                    output[-1].setColumnIndex(ix=0,iy=columnnames.index(coln),iey=None)
                    break
            for name in columnnames:
                del data[name]
        else:#only parameters
            output.append(dA(np.zeros(3),XYeYeX=[0,1]))
            output[-1].comment+['only parameters in file']


        #append parameters to result
        for key,item in para.items():
            if key=='MeasurementDateandTime':
                #make a computational time
                timestring=' '.join(item[0].replace(',','').replace('.','').split('\t'))
                tt=time.mktime(time.strptime(timestring,'%A %d %B %Y %H:%M:%S'))
                setattr(output[-1],key.split('(')[0],time.ctime(tt))
                setattr(output[-1],'MeasurementTimeSeconds',tt)
            elif key.split('(')[0]==u'T':
                setattr(output[-1],'Temperature',np.array(item[0],dtype=float))
            else:
                try:
                    setattr(output[-1],key.split('(')[0],np.array(item[0],dtype=float))
                except:
                    setattr(output[-1],key.split('(')[0],item[0])
        try:
            #append distribution if not already above saved
            distributions=dA(np.c_[[np.array(data[name],dtype=float) for name in  columnnames]],XYeYeX=[0,1])
            distributions.columnname=''.join(['%s; ' %(name) for name in  columnnames])
            for coln in names[2:]:
                if coln in columnnames:
                    distributions.setColumnIndex(ix=0,iy=columnnames.index(coln),iey=None)
                    break
            for name in columnnames:
                del data[name]
            output[-1].distributions=distributions
        except: pass
        try:
            distributions=[]
            columnnames=''
            for dist in ['DistributionFitDelayTimes','DistributionFitData','DistributionFit']:
                try:
                    distributions.append(getattr(output[-1],dist))
                    columnnames+=dist+';'
                    delattr(output[-1],dist)
                except: pass
            output[-1].distributionFit=dA(np.r_[distributions].squeeze())
            output[-1].distributionFit.columnames=columnnames
            output[-1].distributionFit.setColumnIndex(iey=None)
            output[-1].distributionFit.comment=['this is g1']
        except: pass
        #append all remaining data to parameters ------------------------------------------------------
        for key in data.keys():
            try:
                setattr(output[-1],key,np.array(data[key],dtype=float))
            except:pass
        output[-1].filename=filename
    #reset locale
    locale.setlocale(locale.LC_TIME, old_loc)
    return output



