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
Structure factors and directly related functions for scattering
related to interaction potentials between particles.

Return values are dataArrays were useful.

To get only Y values use .Y

For RMSA an improved algorithm is used based on the original idea described in [1]_ (see Notes in RMSA).

"""
from __future__ import print_function
from __future__ import division
import sys
import os
import inspect
import math,cmath
import scipy
import scipy.integrate
import scipy.fftpack
import scipy.constants as constants
import scipy.special as special
from .dataarray import dataArray as dA
from .dataarray import dataList as dL
import numpy as np
from . import parallel
from .graceplot import GracePlot as grace
from . import formel
import time
_path_=os.path.realpath(os.path.dirname(__file__))

# variable to allow printout for debugging as if debug:print 'message'
# set it to integer value above debuglevel
debug=False


def _sqcoefOriginalHP(ir,eta,gek,ak,a=0.,b=0.,c=0.,f=0.,u=0.,v=0.,gamk=0.,seta=0.,sgek=0.,sak=0.,scal=0.,g1=0.):
    """
    CALCULATES RESCALED VOLUME FRACTION AND CORRESPONDING COEFFICIENTS
    This is only for documenting the difference to the old algorithm.
                                                                    
    This is the iterative part to find rescaling parameter to get G(1+)>0 (Gillian condition) if G(1+)>0
     
    Returns:       
    ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1                                                   
                                                                    
    seta IS THE RESCALED VOLUME FRACTION.                             
    sgek IS THE RESCALED CONTACT POTENTIAL.                           
    sak IS THE RESCALED SCREENING CONSTANT.                           
    a,b,c,f,u,v ARE THE MSA COEFFICIENTS.                             
    g1=G(1+) IS THE CONTACT VALUE OF G(R/SIG);                        
    FOR THE GILLAN CONDITION, THE DIFFERENCE FROM                     
    ZERO INDICATES THE COMPUTATIONAL ACCURACY.                        
                                                                    
    IR > 0: NORMAL EXIT, IR IS THE NUMBER OF ITERATIONS.              
    < 0: FAILED TO CONVERGE. 
    
    This is equivalent to the original HP Fortran code.
    The different conditions might have saved computing time in 1981.
    For some parameter conditons the rescaling is needed but not done.

    Also for some parameter contributions the wrong root for Fwww is used.

    """
    # set to zero to get debug messages; debuglevel>10 no messages
    debuglevel=1
    itm=40  # original 40
    acc=5.e-6
    if debug>debuglevel: print('-- ')
    if ak>=(1+8.*eta):
        # for large screening (scl is small and ak is large)
        # ix=1  SOLVE FOR LARGE K, RETURN G(1+)
        ix,ir,g1,eta,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1= \
            _sqfun(1,ir,g1,eta,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1,useHP=True)
        if debug>debuglevel: print('large screening ', ir, g1, ak, gamk, 'abcfuv', a, b, c, f, u, v)
        if ir<0 or g1>=0:  # error or already a good solution is returned
            return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
        else:
            # we have to rescale the solution in the later as here g+<0
            pass
    seta=min(eta,0.2)
    if ak>=(1+8.*eta) or gamk>=0.15:
        # find a rescaled eta with g+>=0 for strong coupling or low volume fraction
        j=0.
        f1=0.
        f2=0.
        while True:  # loop for Newton iteration to find g+=0
            j=j+1
            if (j>itm):
                return -1,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
            if (seta<=0.0): seta=eta/j  # g+<0 -> rescale eta
            if (seta>0.6): seta=0.35/j  # rescaled eta>0.6 rescale to smaller value
            e1=seta  # e1 first eta
            # ix=2  RETURN FUNCTION TO SOLVE FOR ETA(GILLAN)
            ix,ir,f1,e1,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1= \
                _sqfun(2,ir,f1,e1,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1,useHP=True)
            e2=seta*1.01              # increase scaled eta
            ix,ir,f2,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1= \
                _sqfun(2,ir,f2,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1,useHP=True)
            e2=e1-(e2-e1)*f1/(f2-f1)  # new approximation for scaled eta
            seta=e2                   # save for next iteration or as result
            delta=abs((e2-e1)/e1)     # relative change
            if delta<acc: break       # if changes are small enough then break
        if debug>debuglevel: print('rescaling with %i iterations leads to scaling by %.3g' % (j, seta / eta))
        # ix=4    RETURN G(1+) FOR ETA=ETA(GILLAN).
        ix,ir,g1,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g11= \
            _sqfun(4,ir,g1,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1,useHP=True)
        ir=j
        ###---------------end of Newton loop
        if debug>debuglevel: print( 'rescaled ',ir,g1,ak,gamk,'abcfuv',a,b,c,f,u,v,'ak>,seta>eta ',ak>=(1+8.*eta), seta>=eta)
        if ak>=(1+8.*eta): # in this case return anyway
            return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
        else:
            if  seta>=eta:  # seta>eta indicates succesfull rescaling with g1 as zero
                return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1

    ix,ir,g1,eta,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1= \
        _sqfun(3,ir,g1,eta,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1,useHP=True)
    if debug>debuglevel: print('after scaling ',ir,g1,ak,gamk,'abcfuv',a,b,c,f,u,v)
    if ir>=0 :
        if g1<0.: ir=-3  # rescaling not successful
    return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1

def _sqcoef(ir,eta,gek,ak,a=0.,b=0.,c=0.,f=0.,u=0.,v=0.,gamk=0.,seta=0.,sgek=0.,sak=0.,scal=0.,g1=0.):
    """
    CALCULATES RESCALED VOLUME FRACTION AND CORRESPONDING COEFFICIENTS

    This is the iterative part to find rescaling parameter to get G(1+)>0 (Gillian condition) if G(1+)>0

    Returns:
    ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1

    seta IS THE RESCALED VOLUME FRACTION.
    sgek IS THE RESCALED CONTACT POTENTIAL.
    sak IS THE RESCALED SCREENING CONSTANT.
    a,b,c,f,u,v ARE THE MSA COEFFICIENTS.
    g1=G(1+) IS THE CONTACT VALUE OF G(R/SIG);
    FOR THE GILLAN CONDITION, THE DIFFERENCE FROM
    ZERO INDICATES THE COMPUTATIONAL ACCURACY.

    IR > 0: NORMAL EXIT, IR IS THE NUMBER OF ITERATIONS.
    < 0: FAILED TO CONVERGE.

    This is a shorter version of sqcoef which is easier to understand and allows
    no bypassing between the conditions in original code which leads to errors for harmless parameter settings.
    The idea is the original idea (see [2]_) to calculate the MSA and to rescale if  g+<0  .


    """
    # set to zero to get debug messages; debuglevel>10 no messages
    debuglevel=1
    itm=80  # original 40
    acc=5.e-6
    fix=0.5
    if debug>debuglevel: print('-- ')
    # just try to solve
    ix,ir,g1,eta,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1= \
        _sqfun(1,ir,g1,eta,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1)
    if debug>debuglevel: print('first try ',ir,g1,ak,gamk,'abcfuv',a,b,c,f,u,v)
    if (ir == -2):
        # FAILED TO CONVERGE in Newton algorith to find zero, only in classical HP solution,
        return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
    elif (ir == -4):
        # no root found in first try
        return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
    elif (g1<0):
        # we have to rescale the solution in the later as here g+<0
        pass
    elif (g1>=0):  # already a good solution is returned
        return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1

    seta=min(eta,0.2)
    # find a rescaled eta with g+>=0 for strong coupling or low volume fraction
    j=0.
    f1=0.
    f2=0.
    while True:  # loop for Newton iteration to find g+=0
        j=j+1
        if (j>itm):
            return -1,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
        if (seta<=0.0): seta=eta/j  # g+<0 -> rescale eta
        if (seta>0.6): seta=0.35/j  # rescaled eta>0.6 rescale to smaller value
        e1=seta  # e1 first eta
        # ix=2  RETURN FUNCTION TO SOLVE FOR ETA(GILLAN)
        ix,ir,f1,e1,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1= \
            _sqfun(2,ir,f1,e1,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1)
        e2=seta*1.01  # increase scaled eta
        ix,ir,f2,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1= \
            _sqfun(2,ir,f2,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1)
        e2=e1-(e2-e1)*f1/(f2-f1)  # new approximation for scaled eta
        seta=e2  # save for next iteration or as result
        delta=abs((e2-e1)/e1)  # relative change
        if delta<acc: break  # changes  are small enough then break
    if debug>debuglevel: print('rescaling with %i iterations leads to scaling by %.3g'%(j,seta/eta))
    # ix=4    RETURN G(1+) FOR ETA=ETA(GILLAN) with all parameters.
    ix,ir,g1,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g11= \
        _sqfun(4,ir,g1,e2,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1)
    if (seta>0.64) or (seta<eta):
        ir=-3  # rescaling not successful
        return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
    ir=j
    ###---------------end of Newton loop
    if debug>debuglevel: print('rescaled ',ir,g1,ak,gamk,'abcfuv',a,b,c,f,u,v,'ak>,seta,eta ',ak>=(fix+8.*eta), seta,eta)
    return ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1


def _sqfun(ix,ir,fval,evar,reta,rgek,rak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1,useHP=False):
    """
    CALCULATES VARIOUS COEFFICIENTS AND FUNCTION VALUES FOR _sqcoef                            
    
    this is the NOT rescaled solution! == MSA

    Options
    ix =1: SOLVE FOR LARGE K, RETURN G(1+).                            
        2: RETURN FUNCTION TO SOLVE FOR ETA(GILLAN).                     
        3: ASSUME NEAR GILLAN, SOLVE, RETURN G(1+).                      
        4: RETURN G(1+) FOR ETA=ETA(GILLAN).                             

    SETA IS THE RESCALED VOLUME FRACTION.                             
    SGEK IS THE RESCALED CONTACT POTENTIAL.                           
    SAK IS THE RESCALED SCREENING CONSTANT.                           
    A,B,C,F,U,V ARE THE MSA COEFFICIENTS.                             
    G1=G(1+) IS THE CONTACT VALUE OF G(R/SIG);                        
    FOR THE GILLAN CONDITION, THE DIFFERENCE FROM                     
    ZERO INDICATES THE COMPUTATIONAL ACCURACY.                        
                                                                      
    IR > 0: NORMAL EXIT, IR IS THE NUMBER OF ITERATIONS.              
     < 0: FAILED TO CONVERGE.                                         

    The root of the quartic F = w4*fa**4+w3*fa**3+w2*fa**2+w1*fa+w0 needs to be found.
    in this code we have two choices in the source code.
    One for documentation and the second as the correct solution:

     1. to use the original HayterPenfold algorithm from the Fortran code as also eg used in SASVIEW and SASFIT
        with an estimate for the root of Fwww which is refined by Newton algorithm
        which results under specific conditions in the wrong root
        test with e.g.
        for scl in np.r_[1:10]:p.plot(js.sf.RMSA(q=x,R=3.1,scl=scl, gamma=1.1, eta=0.5),legend='%.3g' %scl)
        the correct branch can be verified by using the PercusYevivk as limit

     2. original idea from Hayter paper [1]_ as *default  solution*
        find all roots (by numpy.roots) and take the physical root with g(r/diameter<1)=0
        in this code there is no difference between ix=1 and 3
        with structurefactor.debug=11 you get output for g(r) and the zeros of Fwww (see source code)



    """
    # set to zero to get debug messages; debuglevel>10 no messages
    debuglevel=1
    acc=1e-6  # stop criterion for Newton
    itm=40  # max number of iterations
    # needed parameters with changes for iteration
    eta=evar  # volume fraction
    scal=(reta/evar)**(1/3.)  # scaling factor
    sak=rak/scal  # scaled dimensionless screening constant
    val=rgek if abs(rgek)>1e-9 else 1e-9  # prevent zero and just take small value
    sgek=val*scal*math.exp(rak-sak)  # scaled contact potential
    gek=sgek
    ak=sak
    # -----------------reproduce original fortran code
    # using these variables is important to reduce the dependency on accuracy of float64
    # and maybe it makes it a bit faster
    eta2=eta**2
    eta3=eta2*eta
    e12=12.*eta
    e24=e12+e12
    ak2=ak**2
    ak1=1+ak
    dak2=1.0/ak2
    dak4=dak2*dak2
    d=1-eta
    d2=d*d
    dak=d/ak
    dd2=1.0/d2
    dd4=dd2*dd2
    dd45=dd4*2.0e-1
    eta3d=3.*eta
    eta6d=eta3d+eta3d
    eta32=eta3+eta3
    eta2d=eta+2.0
    eta2d2=eta2d*eta2d
    eta21=2.0*eta+1.0
    eta22=eta21*eta21

    # all coefficients from appendix in the paper [1]
    al1=-eta21*dak
    al2=(14*eta2-4*eta-1)*dak2
    al3=36*eta2*dak4

    b1=-(eta2+7.*eta+1.)*dak
    b2=9.*eta*(eta2+4.*eta-2.)*dak2
    b3=12.*eta*(2*eta2+8.*eta-1.)*dak4

    n1=-(eta3+3.*eta2+45.*eta+5.)*dak
    n2=(eta32+3.*eta2+42.*eta-20.)*dak2
    n3=(eta32+30.*eta-5.)*dak4
    n4=n1+24.*eta*ak*n3
    n5=eta6d*(n2+4.*n3)

    f1=eta6d/ak
    f2=d-12.*eta*dak2

    ff1=f1*f1
    ff2=f2*f2
    ff=ff1+ff2
    f1f2=2.*f1*f2

    t1=(eta+5.)/(5.*ak)
    t2=eta2d*dak2
    t3=-12.*eta*gek*(t1+t2)
    t4=eta3d*ak2*(t1*t1-t2*t2)
    t5=eta3d*(eta+8.)*0.1-2.*eta22*dak2
    # ------------
    a1=(e24*gek*(al1+al2+ak1*al3)-eta22)*dd4
    bb1=(1.5*eta*eta2d2-12.*eta*gek*(b1+b2+ak1*b3))*dd4
    v1=(eta21*(eta2-2.*eta+10.)*0.25-gek*(n4+n5))*dd45
    p1=(gek*(ff1+ff2-f1f2)-0.5*eta2d)*dd2
    T1=t3+t4*a1+t5*bb1

    if (sak>15) and (ix==1):
        if debug>debuglevel: print('(sak>15) and (ix==1)',ak)
        # this corresponds to ibig=1 in original Hayter-Penfold code for large screening
        # large screening means the screenig length 1/kappa is small compared to 2R and we are in the hard sphere limit
        # if ak is big -> cosh = sinh and a lot simplifies in asymptotic solution
        # but at same time cosh(ak) may exceeds numerical limits for really large ak
        a3=e24*(eta22*dak2-0.5*d2-al3)*dd4
        bb3=e12*(0.5*d2*eta2d-eta3d*eta2d2*dak2+b3)*dd4
        v3=((eta3-6.*eta2+5.)*d-eta6d*(2.*eta3-3.*eta2+18.*eta+10.)*dak2+e24*n3)*dd45
        p3=(ff1-ff2)*dd2
        T3=t4*a3+t5*bb3+e12*t2-0.4*eta*(eta+10.)-1.
        M6=T3*a3-e12*v3*v3
        M5=T1*a3+a1*T3-e24*v1*v3
        M4=T1*a1-e12*v1*v1
        L6=e12*p3*p3
        L5=e24*p1*p3-2.*bb3-ak2
        L4=e12*p1*p1-2.*bb1
        W56=M5*L6-L5*L6
        W46=M4*L6-L4*M6
        fa=-W46/W56
        ca=-fa
        f=fa
        c=ca
        b=bb1+bb3*fa
        a=a1+a3*fa
        v=v1+v3*fa
        g1=-(p1+p3*fa)
        fval=g1 if g1>1e-3 else 0.
        seta=evar
        # g24 = e24*gek*math.exp(ak)            # prevent math range error in exp for large ak (-> small scl)
        # u = (ak2*ak*ca-g24)/(ak2*g24)         # so we rewrite this to have exp(-ak)
        u=ak*ca/e24/gek*math.exp(-ak)-1/ak2     # same as above two lines but this prevents math range error
        return ix,ir,fval,evar,reta,rgek,rak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1

    # small sak for the remaining
    sk=math.sinh(ak)
    ck=math.cosh(ak)
    ckma=ck-1.-ak*sk
    skma=sk-ak*ck
    a2=e24*(al3*skma+al2*sk-al1*ck)*dd4
    a3=e24*(eta22*dak2-0.5*d2+al3*ckma-al1*sk+al2*ck)*dd4

    bb2=e12*(-b3*skma-b2*sk+b1*ck)*dd4
    bb3=e12*(0.5*d2*eta2d-eta3d*eta2d2*dak2-b3*ckma+b1*sk-b2*ck)*dd4

    v2=(n4*ck-n5*sk)*dd45
    v3=((eta3-6.*eta2+5.)*d-eta6d*(2.*eta3-3.*eta2+18.*eta+10.)*dak2+e24*n3+n4*sk-n5*ck)*dd45
    # define...
    p2=(ff*sk+f1f2*ck)*dd2
    p3=(ff*ck+f1f2*sk+ff1-ff2)*dd2

    T2=t4*a2+t5*bb2+e12*(t1*ck-t2*sk)
    T3=t4*a3+t5*bb3+e12*(t1*sk-t2*(ck-1.))-0.4*eta*(eta+10.)-1.

    M1=T2*a2-e12*v2*v2
    M2=T1*a2+T2*a1-e24*v1*v2
    M3=T2*a3+T3*a2-e24*v2*v3
    M4=T1*a1-e12*v1*v1
    M5=T1*a3+T3*a1-e24*v1*v3
    M6=T3*a3-e12*v3*v3

    # ix is defined from the _sqcoef
    #  large k or close to GILLAN CONDITION g1==0 as explained in [1]
    if ix==1 or ix==3:
        # YES - G(X=1+) = 0
        # COEFFICIENTS AND FUNCTION VALUE
        L1=e12*p2*p2
        L2=e24*p1*p2-2.*bb2
        L3=e24*p2*p3
        L4=e12*p1*p1-2.*bb1
        L5=e24*p1*p3-2.*bb3-ak2
        L6=e12*p3*p3

        W16=M1*L6-L1*M6
        W15=M1*L5-L1*M5
        W14=M1*L4-L1*M4
        W13=M1*L3-L1*M3
        W12=M1*L2-L1*M2
        W26=M2*L6-L2*M6
        W25=M2*L5-L2*M5
        W24=M2*L4-L2*M4
        W36=M3*L6-L3*M6
        W35=M3*L5-L3*M5
        W34=M3*L4-L3*M4
        W32=M3*L2-L3*M2
        W46=M4*L6-L4*M6
        W56=M5*L6-L5*M6

        #####QUARTIC COEFFICIENTS W(I)
        #  these are used in
        # fun = w0+(w1+(w2+(w3+w4*fa)*fa)*fa)*fa  =w4*fa**4+w3*fa**3+w2*fa**2+w1*fa+w0
        w4=W16*W16-W13*W36
        w3=2.*W16*W15-W13*(W35+W26)-W12*W36
        w2=W15*W15+2.*W16*W14-W13*(W34+W25)-W12*(W35+W26)
        w1=2.*W15*W14-W13*W24-W12*(W34+W25)
        w0=W14*W14-W12*W24
        # now find root of fun
        if useHP:
            # this documents the original HayterPenfold algorithm as found in original fortran code
            # to find the correct root an estimate is used and refined by Newton method
            # fails eg for R=3.1 gam=1.1 eta=0.5 when scl 6.1999 -> 6,2 as sak changes over 1
            # or scl=1.37382379588 R=2.5 gam=5.1 eta=0.6 as the found root results in g(r<1)>0
            # reason: in Newton refining an arbitrary root is found
            if (ix==1):  # large screening
                # LARGE K estimate for the zero of Fwwww
                fap=(W14-W34-W46)/(W12-W15+W35-W26+W56-W32)
            else:  # ix=3  no large screening
                # ASSUME NOT TOO FAR FROM GILLAN CONDITION.
                # IF BOTH RGEK AND RAK ARE SMALL, USE P-W ESTIMATE.of the zero of Fwwww
                g1=0.5*eta2d*dd2*math.exp(-gek)
                pg=p1+g1
                ca=ak2*pg+2.*(bb3*pg-bb1*p3)+e12*g1*g1*p3
                ca=-ca/(ak2*p2+2.*(bb3*p2-bb2*p3))
                fap2=-(pg+p2*ca)/p3
                if ((gek>0) and (sgek<=2.0) and (sak<=1.0)):
                    # gek>0 as this is only for positive contact potentials
                    #this was introduced in the SASFIT conversion (C code)
                    e24g=e24*gek*math.exp(ak)
                    pwk=math.sqrt(e24g)
                    qpw=(1.-math.sqrt(1.+2.*d2*d*pwk/eta22))*eta21/d
                    g1=-qpw*qpw/e24+0.5*(eta2d)*dd2
                pg=p1+g1
                ca=ak2*pg+2.*(bb3*pg-bb1*p3)+e12*g1*g1*p3
                ca=-ca/(ak2*p2+2.*(bb3*p2-bb2*p3))
                fap=-(pg+p2*ca)/p3
                # print('PWEstimate',fap,fap2,( sgek<=2.0) and ( sak<=1.0))
            # now find a better estimate of the zero by Newton iteration
            # RB: this algorithm finds different roots dependent on sgek and sak
            # the roots are somehow arbitrary in the 4 possible ones,
            # the main time it is one of the two centered which make no big jumps but the outer ones make large jumps in the result
            ii=0
            while True:
                ii=ii+1
                if (ii>itm):  # FAILED TO CONVERGE IN ITM ITERATIONS
                    ir=-2
                    return ix,ir,fval,evar,reta,rgek,rak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1
                fa=fap  # estimated zero pole of fun
                fun=w0+(w1+(w2+(w3+w4*fa)*fa)*fa)*fa    # function to minimize
                fund=w1+(2.*w2+(3.*w3+4.*w4*fa)*fa)*fa  # derivative of fun
                fap=fa-fun/fund                         # new value as next estimate
                if fa==0: continue                      # fa is 0 if gek is zero
                delta=abs((fap-fa)/fa)                  # difference
                if delta<acc: break
            # found one and use this zero
            ir=ir+ii
            fa=fap
            ca=-(W16*fa*fa+W15*fa+W14)/(W13*fa+W12)
            g1=-(p1+p2*ca+p3*fa)
        else:
            # original idea from Hayter paper [1]_
            # take all roots and use the physical root with g(r/diameter<1)=0
            # in this code there is no difference between ix=1 or 3
            # The algorithm relies on computing the eigenvalues of the companion matrix
            x0=np.roots([w4,w3,w2,w1,w0])  # 114µs      slower than direct calculation, but this is not the bottle neck
            if np.all((x0.imag/x0.real)<1e-3):
                # if the imaginary part of complex roots is small use also these
                # in some cases this is the correct solution in gr
                fa=x0.real
            else:
                fa=x0[np.isreal(x0)].real   # 6.5µs
            fa.sort()  # we have up to 4 real roots and each of the following has up to 4 values
            ca=-(W16*fa*fa+W15*fa+W14)/(W13*fa+W12)
            g1=-(p1+p2*ca+p3*fa)
            b=bb1+bb2*ca+bb3*fa
            a=a1+a2*ca+a3*fa
            # choose the correct root by calculating g(r) (sin transform) and using the one with g(r<1)=0
            # here i choose explicitly 1-delta
            delta=0.05
            nn=(2**13+0)                                    # n number of points to get reliable fft
            dqr2=np.r_[0,delta:nn*delta:delta]              # points to calculate S(dqr2)
            kk=1//delta                                     # index of last point smaller 1
            # calc the valueof g(x) with x=1-delta=kk*delta  in equ.12 of[1]_
            gr1=[delta*np.sum((_SQMSA(dqr2,scal,eta,ak,gek,aa,bb,cca,ffa)-1)*dqr2*np.sin(kk*delta*dqr2))
                                      for aa,bb,cca,ffa in zip(a,b,ca,fa)]
            grval=[1+ggr/(12*np.pi*eta*kk*delta) for ggr in gr1]
            if len(fa)==0 or np.min(grval)>0.1:
                # no real root found or not grval close to zero
                ir = -4
                return ix,ir,fval,evar,reta,rgek,rak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1.max() if np.size(g1) else g1
            # chose the one with grval close to zero
            chooseone=np.argmin(np.abs(grval))
            if debug>debuglevel:
                # this writes the calculated g(r) to a file for checking of g(r)
                rrr=2*np.pi*np.fft.rfftfreq(len(dqr2),d=delta)  # points in r domain from rfft r/diameter
                # doing sin transform with rfft results in minus in front of imag part compared to equation 12 in HP paper [1]
                # delta* is to get correct integral
                #gr=[delta*np.fft.rfft((_SQMSA(dqr2,scal,eta,ak,gek,aa,bb,cca,ffa)-1)*dqr2).imag
                #                                            for aa,bb,cca,ffa in zip(a,b,ca,fa)]
                gr=[delta*scipy.fftpack.dst(_SQMSA(dqr2,scal,eta,ak,gek,aa,bb,cca,ffa)-1)*dqr2
                                                            for aa,bb,cca,ffa in zip(a,b,ca,fa)]
                # [1:] to avoid rrr=zero
                gr=[1-ggr[1:]/(12*np.pi*eta*rrr[1:]) for ggr in gr]
                # choose one with minimum mean value g(r) for rrr<1 which should be zero
                # above we use only one value and choose smallest grval
                # here we choose the smallest mean value which is often not correct but here it is only for demo
                grval=[grr[rrr[1:]<0.9][1:].mean() for grr in gr]
                print('grval  ',grval)
                temp=dL()
                for i,grr in enumerate(gr):
                    temp.append(np.c_[rrr[1:],grr].T)
                    temp[-1].choosen=chooseone
                    temp[-1].zero=fa[i]
                    temp[-1].g1=g1[i]
                    temp[-1].legend='g(r<1)= %.3g' %(grval[i])
                temp.savetxt('testgr.dat')
                print('zeros,g1,choosen zero',fa,g1,chooseone)
            fa=fa[chooseone]
            ca=ca[chooseone]
            g1=-(p1+p2*ca+p3*fa)
            # end searching the root- recalculating final result------------------------
        fval=(g1 if abs(g1)>1e-3 else 0.)
        seta=evar
        f=fa
        c=ca
        b=bb1+bb2*ca+bb3*fa
        a=a1+a2*ca+a3*fa
        v=(v1+v2*ca+v3*fa)/a

    else:
        # -> ix==2 or ix==4
        ca=ak2*p1+2.*(bb3*p1-bb1*p3)
        ca=-ca/(ak2*p2+2.0*(bb3*p2-bb2*p3))
        fa=-(p1+p2*ca)/p3
        # fval will contain g1 for Newton iteration ix=2,4
        if ix==2:    fval=M1*ca*ca+(M2+M3*fa)*ca+M4+M5*fa+M6*fa*fa
        if ix==4:    fval=-(p1+p2*ca+p3*fa)
        f=fa
        c=ca
        b=bb1+bb2*ca+bb3*fa
        a=a1+a2*ca+a3*fa
        v=(v1+v2*ca+v3*fa)/a
    g24=e24*gek*math.exp(ak)
    u=(ak2*ak*ca-g24)/(ak2*g24)
    return ix,ir,fval,evar,reta,rgek,rak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1


def _SQMSA(qR2,scal,eta,ak,gek,a,b,c,f):
    """
    equation 14 Hayter-Penfold paper [1] in sfRMSA to calculate the final structure factor
    """
    K=np.where(qR2==0,1e-15,qR2/scal) # catch zero
    if ak>25:  # c==-f and
        # avoid to large ak to prevent math range error
        # ak>15 has f=-c from sqfun so the sinh and cosh terms cancel for large ak
        sinhsk=0.
        coshsk=0.
    else:
        sinhsk=math.sinh(ak)
        coshsk=math.cosh(ak)
    sink=np.sin(K)
    cosk=np.cos(K)
    K2=K*K
    K3=K2*K
    K4=K3*K
    KK2ak2=1/K/(K2+ak**2)
    a_K=a*(sink-K*cosk)/K3 \
        +b*((2./K**2-1)*K*cosk+2*sink-2./K)/K3 \
        +a*eta*(24./K3+4.*(1-6./K2)*sink-(1-12./K2+24./K4)*K*cosk)/2./K3 \
        +c*(ak*coshsk*sink-K*sinhsk*cosk)*KK2ak2 \
        +f*(ak*sinhsk*sink-K*(coshsk*cosk-1))*KK2ak2 \
        +f*(cosk-1)/K2 \
        -gek*(ak*sink+K*cosk)*KK2ak2
    msa=1/(1-24.*eta*a_K)
    MSA=np.where(qR2==0,-1/a,msa)   # -1/a is correct solution for qR2==zero
    return MSA


def RMSA(q, R, scl, gamma, molarity=None, eta=None,useHP=False):
    """
    Structure factor for a screened coulomb interaction in rescaled mean spherical approximation (RMSA).
    
    Structure factor according to Hayter-Penfold [1]_ [2]_ .
    Consider a scattering system consisting of macro ions, counter ions  and solvent.
    Here an improved algorithm is used based on the original idea described in [1]_ (see Notes).
   
    Parameters
    ----------
    q : array; N dim
        Scattering vector; units 1/nm
    R : float
        Radius of the object; units nm
    molarity : float
        Number density n in units mol/l. Overides eta, if both given.
    scl : float>0
        Screening length; units nm; negative values evaluate to scl=0.
    gamma : float    
        | contact potential; units kT
        | gamma=Zm/(pi*e0*e*R*(2+k*R))
        |   Zm = Z* effective surface charge
        |   e0,e free permittivity and dielectric constant
        |   k=1/scl inverse screening length of Debye-Hückel potential
    eta : float
        Volume fraction as eta=4/3*pi*R**3*n  with number density n.
    useHP : True, default False
        To use the original Hayter/Penfold algorithm. This gives wrong results for some parameter conditions.
        It should ONLY be used for testing.
        See example examples/test_newRMSAAlgorithm.py for a direct comparison.

    Returns
    -------
    dataArray : .
     - .volumeFraction = eta
     - .rescaledVolumeFraction
     - .screeningLength
     - .gamma=gamma
     - .contactpotential
     - .S0 structure factor at q=0
     - .scalingfactor factor for rescaling to get g+1=0; if =1 nothing was scaled and it is MSA
                                                                    
    Notes
    -----
    Improved algorithm
     The Python code is deduced from the original Hayter-Penfold Fortran code (1981, ILL Grenoble).
     This is also used in other common SAS programs as SASfit or SASview (translated to C).
     The original algorithm determines the root of a quartic F(w1,w2,w3,w4) by an estimate (named PW estimate),
     refining it by a Newton algorithm. As the PW estimate is somtimes not good enough this results in an
     arbitrary root of the quartic in the Newton algorithm. The solution therefore jumps between different
     posibilities by small changes of the parameters.
     We use here the original idea from [1]_ to calculate G(r<0) for all four roots of F(w1,w2,w3,w4) and use
     the physical solution with G(r<R)=0.
     See examples/test_newRMSAAlgorithm.py for a direct comparison.

    Validity
     The calculation of charge at the surface or screening length from a solute ion concentration is explicitly dedicate
     to the user. The Debye-Hückel theory for a macro ion in screened solution is a far field theory as a linearization
     of the Poisson-Boltzmann (PB) theory and from limited validity (far field or low charge -> linearization).
     Things like reverting charge layer, ion condensation at the surface, pH changes at the surface or other things
     might appear. Before calculating please take these things into account. Close to the surface the PB has to be solved.
     The DH theory can still be used if the charge is thus an effective charge named Z*, which might be different from the
     real surface charge.
     See Ref [3]_ for details.


    References
    ----------    
    .. [1] J. B. Hayter and J. Penfold, Mol. Phys. 42, 109 (1981).
    .. [2] J.-P. Hansen and J. B. Hayter, Mol. Phys. 46, 651 (2006).
    .. [3] L. Belloni, J. Phys. Condens. Matter 12, R549 (2000).
    
    """

    """
    Original Doc of the Hayter Penfold Fortran routine::
        
    seta is the rescaled volume fraction.                             
    sgek is the rescaled contact potential.                           
    sak is the rescaled screening constant.                           
    a,b,c,f,u,v are the msa coefficients.                             
    g1=g(1+) is the contact value of g(r/sig);                        
    for the Gillan condition, the difference from                     
    zero indicates the computational accuracy.                        

      ROUTINE TO CALCULATE S(Q*SIG) FOR A SCREENED COULOMB
      POTENTIAL BETWEEN FINITE PARTICLES OF DIAMETER 'SIG'
      AT ANY VOLUME FRACTION. THIS ROUTINE IS MUCH MORE POWER-
      FUL THAN "SQHP" AND SHOULD BE USED TO REPLACE THE LATTER
      IN EXISTING PROGRAMS. NOTE THAT THE COMMON AREA IS
      CHANGED; IN PARTICULAR, THE POTENTIAL IS PASSED
      DIRECTLY AS 'GEK' = GAMMA*EXP(-K) IN THE PRESENT ROUTINE.
      JOHN B.HAYTER (I.L.L.) 19-AUG-81
 
      CALLING SEQUENCE:
       CALL SQHPA(QQ,SQ,NPT,IERR)
 
      QQ: ARRAY OF DIMENSION NPT CONTAINING THE VALUES  OF Q*SIG AT WHICH S(Q*SIG) WILL BE CALCULATED.
      SQ: ARRAY OF DIMENSION NPT INTO WHICH VALUES OF  S(Q*SIG) WILL BE RETURNED.
      NPT: NUMBER OF VALUES OF Q*SIG.
 
      IERR > 0: NORMAL EXIT; IERR=NUMBER OF ITERATIONS.
       -1: NEWTON ITERATION NON-CONVERGENT IN "SQCOEF"
       -2: NEWTON ITERATION NON-CONVERGENT IN "SQFUN".
       -3: CANNOT RESCALE TO G(1+) > 0.
 
      ON ENTRY:
      ETA: VOLUME FRACTION
      GEK: THE CONTACT POTENTIAL GAMMA*EXP(-K)
      AK: THE DIMENSIONLESS SCREENING CONSTANT
      AK = KAPPA*SIG WHERE KAPPA IS THE INVERSE SCREENING
      LENGTH AND SIG IS THE PARTICLE DIAMETER.
 
      ON EXIT:
      GAMK IS THE COUPLING: 2*GAMMA*S*EXP(-K/S), S=ETA**(1/3).
      SETA, SGEK AND SAK ARE THE RESCALED INPUT PARAMETERS.
      SCAL IS THE RESCALING FACTOR: (ETA/SETA)**(1/3).
      G1=G(1+), THE CONTACT VALUE OF G(R/SIG).
      A,B,C,F,U,V ARE THE CONSTANTS APPEARING IN THE ANALYTIC
      SOLUTION OF THE MSA (HAYTER-PENFOLD; MOL.PHYS. 42: 109 (1981))
 
      NOTES:
      (A) AFTER THE FIRST CALL TO SQHPA, S(Q*SIG) MAY BE EVALUATED
      AT OTHER Q*SIG VALUES BY REDEFINING THE ARRAY QQ AND CALLING
      "SQHCAL" DIRECTLY FROM THE MAIN PROGRAM.
      (B) THE RESULTING S(Q*SIG) MAY BE TRANSFORMED TO G(R/SIG)
      USING THE ROUTINE "TROGS".
      (C) NO ERROR CHECKING OF INPUT PARAMETERS IS PERFORMED;
      IT IS THE RESPONSIBILITY OF THE CALLING PROGRAM TO VERIFY
      VALIDITY.
      SUBROUTINES REQUIRED BY SQHPA:
      (1) SQCOEF RESCALES THE PROBLEM AND CALULATES THE
       APPROPRIATE COEFFICIENTS FOR "SQHCAL".
      (2) SQFUN CALCULATES VARIOUS VALUES FOR "SQCOEF".
      (3) SQHCAL CALCULATES H-P S(Q*SIG) GIVEN A,B,C,F.


    """
    R=abs(R)
    error={-1: 'NEWTON ITERATION NON-CONVERGENT IN _sqcoef',
           -2: 'NEWTON ITERATION NON-CONVERGENT IN _sqfun',
           -3: 'CANNOT RESCALE TO G(1+) > 0.',
           -4: 'no physical root with G(r<1) < 0.1 in _sqfun found'} # added for new algorithm
    # get volume fraction eta from number density and radius R
    if isinstance(molarity,(float,int)):
        molarity=abs(molarity)
        numdens=constants.N_A*molarity*1e-24  # from mol/l to particles/nm**3
        eta=4/3.*np.pi*R**3*numdens
    elif isinstance(eta,(float,int)):
        numdens=eta/(4/3.*np.pi*R**3)
        molarity=numdens/(constants.N_A*1e-24)
    else:
        raise Exception('one of molarity/eta needs to be given.')    # dimensionless screening constant ak
    if eta <= 0.: eta = 1e-10
    #if eta>1:        raise Exception('eta needs to be smaller 1.')
    if scl<=0:
        ak=1e20
    else:
        ak=2*R/scl
    # to large ak make math error in exp , anyway then we have a hard sphere
    if ak>200:ak=200
    # the contact potential in kT
    gek=gamma*math.exp(-ak)
    # coupling
    gamk=2.*eta**(1/3.)*gek*math.exp(ak-ak/eta**(1/3.))
    # ----------do the rescaling in _sqcoef--------------------
    # _sqcoef does the rescaling to satisfy the Gillian condition with g1==0 according to [2]
    # therein _sqfun calculates the NOT rescaled solution described in [1]
    if useHP:
        ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1=_sqcoefOriginalHP(ir=0,eta=eta,gek=gek,ak=ak,gamk=gamk)
    else:
        ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1=_sqcoef(ir=0,eta=eta,gek=gek,ak=ak,gamk=gamk)
    # catch error
    if ir<0:
        print(ir,error[ir],'g+ =',g1,'ak=',ak)
        return ir

    # dimensionless q scale
    q=np.atleast_1d(q)
    qR2=2*R*q
    # calc values by _SQMSA
    sq=_SQMSA(qR2,scal,seta,sak,sgek,a,b,c,f)
    result=dA(np.r_[[q,sq]])
    result.setColumnIndex(iey=None)
    # add important parameters
    result.volumeFraction=eta
    result.rescaledVolumeFraction=seta
    result.molarity=molarity
    result.screeningLength=scl
    result.gamma=gamma
    result.contactpotential=gek
    result.S0=-1/a
    result.scalingfactor=scal
    result.gplus1=[g1,ir]
    result.modelname=inspect.currentframe().f_code.co_name
    result._coefficients={key: value for (value,key ) in zip([ir,eta,gek,ak,a,b,c,f,u,v,gamk,seta,sgek,sak,scal,g1],
                                        ['ir','eta','gek','ak','a','b','c','f','u','v','gamk','seta','sgek','sak','scal','g1'])}
    return result


def sq2gr(Sq,R,interpolatefactor=2):
    r"""
    Radial distribution function g(r) from structure factor Sq.

    The result strongly depends on quality of S(Q) (number of data points, Q range, smoothness).
    Read [2]_ for details of this inversion problem and why it may fail.

    Parameters
    ----------
    Sq : dataArray
        Structure factor e.g. in units as [Q]=1/nm
         - .X wavevector
         - .Y structure factor
    R : float
        Estimate for the radius of the particles.
    interpolatefactor : int
        Number of points between points in interpolation for rfft.
        2 doubles the points

    Returns
    -------
        dataArray
            .n0  approximated from :math:`2\pi^2 n_0=\int_0^{Q_{max}}  [S(Q) -1]Q^2 dQ`

    Notes
    -----
    One finds that

    .. math:: g(r)-1=(2\pi^2 n_0 r)^{-1} \int_0^\infty  [S(Q) -1]Qsin(qr)dQ

    with :math:`2\pi^2 n_0=\int_0^\infty  [S(Q) -1]Q^2 dQ` defining :math:`n_0`.

    As we have only a limited Q range (:math:`0 < Q < \infty` ), limited accuracy and number of Q values
    we require that :math:`mean(g(R/2<r<R3/4))=0`.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     p=js.grace()
     p.multi(2,1)
     q=js.loglist(0.01,100,2**13)
     p[0].clear();p[1].clear()
     R=2.5
     eta=0.3;scl=5
     n=eta/(4/3.*np.pi*R**3)   # unit 1/nm**3
     sf=js.sf.RMSA(q=q,R=R,scl=scl, gamma=50, eta=eta)
     gr=js.sf.sq2gr(sf,R,interpolatefactor=1)
     sfcut=js.sf.RMSA(js.loglist(0.01,10,2**10),R=R,scl=scl, gamma=50, eta=eta)
     grcut=js.sf.sq2gr(sfcut,R,interpolatefactor=5)
     p[0].plot(sf.X*2*R,sf.Y,le=r'\xG=50')
     p[1].plot(gr.X/2/R,gr[1],le=r'\xG=50')
     p[1].plot(grcut.X/2/R,grcut[1],le=r'\xG=50 \f{}Q\smax\N=10')
     sfh=js.sf.RMSA(q=q,R=R,scl=scl, gamma=0.01, eta=eta)
     grh=js.sf.sq2gr(sfh,R,interpolatefactor=1)
     p[0].plot(sfh.X*2*R,sfh.Y,le=r'\xG=0.01')
     p[1].plot(grh.X/2/R,grh[1],le=r'\xG=0.01')
     p[0].xaxis(max=20,label='2RQ')
     p[1].xaxis(max=4*R,label='r/(2R)')
     p[0].yaxis(max=2,min=0,label='S(Q)')
     p[1].yaxis(max=2.5,min=0,label='g(r)')
     p[0].legend(x=10,y=1.8)
     p[1].legend(x=4,y=1.8)
     p[0].title('Comparison RMSA')
     p[0].subtitle('R=%.2g, eta=%.2g, scl=%.2g' %(R,eta,scl))

    References
    ----------
    .. [1] Yarnell, J. L., Katz, M. J., Wenzel, R. G., & Koenig, S. H. (1973).
           Structure factor and radial distribution function for liquid argon at 85 K.
           Physical Review A, 7(6), 2130.
    .. [2] On the determination of the pair correlation function from liquid structure factor measurements
            A.K. Soper Chemical Physics 107, 61-74, (1986)

    """
    nn=interpolatefactor*Sq.X.shape[0]
    delta=Sq.X.max()/nn
    Q=np.r_[0:Sq.X.max():1j*nn]
    rrr=2*np.pi*scipy.fftpack.fftfreq(nn,delta)[1:nn//2]
    # interpolation for more or smoother points
    Yminus1=np.interp(Q,Sq.X,Sq.Y-1)
    #Yminus1=scipy.interpolate.interp1d(Sq.X,Sq.Y-1,kind=2)(Q)
    #  doing sine transform to solve the sin integral
    Sqdst=scipy.fftpack.dst(Yminus1*Q)
    gr=1/(2*np.pi**2*rrr)*Sqdst[2::2]/(2*np.pi)
    #grminus=1/(2*np.pi**2*rrr)*Sqdst[3::2]/(2*np.pi)
    n0=-1/(2*np.pi**2)*scipy.integrate.simps(Sq.X**2*(Sq.Y-1),Sq.X)
    factor=abs(gr[abs(rrr-R)<R/2].mean())
    gr=1+gr/factor
    #grminus=1+grminus/factor
    result=dA(np.c_[rrr,gr].T)
    result.n0=n0
    result.modelname=inspect.currentframe().f_code.co_name
    return result


def PercusYevick(q,R,molarity=None,eta=None):
    """
    The Percus-Yevick structure factor.
    
    Structure factor for the potential U(r)= (inf for 0<r<R) and (0 for R<r).
    
    Parameters
    ----------
    q : array; N dim
        scattering vector; units 1/(R[unit])
    R : float
        Radius of the object
    eta : float
        volume fraction as eta=4/3*pi*R**3*n  with number density n in units or R
    molarity : float
        number density in mol/l and defines q and R units to 1/nm and nm to be correct 
        preferred over eta if both given

    Returns
    -------
    dataArray 
        structure factor for given q

    Notes
    -----
    Problem is given in [1]_; solution in [2]_ and best description of the solution is in [3]_.

    References
    ----------
    .. [1] J. K. Percus and G. J. Yevick, Phys. Rev. 110, 1 (1958).
    .. [2] M. S. Wertheim, Phys. Rev. Lett. 10, 321 (1963).
    .. [3] D. J. Kinning and E. L. Thomas, Macromolecules 17, 1712 (1984).

    """
    q=np.atleast_1d(q)
    R=abs(R)
    # get volume fraction eta from number density and radius R
    if isinstance(molarity,(float,int)):
        molarity=abs(molarity)
        numdens=constants.N_A*molarity*1e-24  # from mol/l to particles/nm**3
        eta=4/3.*np.pi*R**3*numdens
    elif isinstance(eta,(float,int)):
        eta=abs(eta)
        numdens=eta/(4/3.*np.pi*R**3)
        molarity=numdens/(constants.N_A*1e-24)
    else:
        raise Exception('one of molarity/eta needs to be given.')
    if R==0 or eta==0:
        Sq=np.ones_like(q)
        a=1.
    else:
        u=q*R*2
        u=np.where(u>=0.01,u,np.ones_like(u)*0.01)  # problems with number limits for to small u and avoid zero
        a=(1+2*eta)**2/(1-eta)**4
        b=-3/2*eta*(eta+2)**2/(1-eta)**4
        UU=(a*(np.sin(u)-u*np.cos(u))+
            b*((2/u**2-1)*u*np.cos(u)+2*np.sin(u)-2/u)+
            eta*a/2*(24/u**3+4*(1-6/u**2)*np.sin(u)-
                     (1-12/u**2+24/u**4)*u*np.cos(u)))
        _Sq=1/(1+24*eta/u**3*UU)
        Sq=np.where(u>0.02,_Sq,np.ones_like(u)/a)  # for low u we use the S(q=0) = 1/a
    result=dA(np.r_[[q,Sq]])
    result.setColumnIndex(iey=None)
    result.modelname=inspect.currentframe().f_code.co_name
    result.eta=eta
    result.molarity=molarity
    result.radius=R
    result.Sq0=1/a
    return result


def PercusYevick2D(q,R=1,eta=0.1,a=None):
    """
    The PercusYevick structure factor in 2D
    
    Structure factor for the potential U(r)= (inf for 0<r<R) and (0 for R<r).
    
    Parameters
    ----------
    q : array; N dim
        scattering vector; units 1/(R[unit])
    R : float, default 1
        Radius of the object
    eta : float, default 0.1
        packing fraction as eta=pi*R**2*n  with number density n
        maximum hexagonal closed = (np.pi*R**2)/(3/2.*3**0.5*a**2)
        Rmax=a*3**0.5/2. with max packing of 0.9069
    a : float, default None
        hexagonal lattice constant
        if not None the packing fraction in hexagonal lattice
        as eta=(np.pi*R**2)/(3/2.*3**0.5*a**2) is used
    
    Returns
    -------
        dataArary

    References
    ----------
    .. [1] Free-energy model for the inhomogeneous hard-sphere fluid in D dimensions:
           Structure factors for the hard-disk (D=2) mixtures in simple explicit form
           Yaakov Rosenfeld Phys. Rev. A 42, 5978
    
    """
    if a!=None:
        eta=(np.pi*R**2)/(3/2.*3**0.5*a**2)
    q=np.atleast_1d(q)
    if R==0 or eta==0:
        Sq=np.ones_like(q)
    else:
        qR=lambda q: q*R
        u=np.piecewise(q,[q==0],[1e-8,qR])  # exchange q=zero with small Q as limit
        Xi=(1+eta)/(1-eta)**3
        G=(1-eta)**-1
        Z=(1-eta)**-2
        A=(1+(2*eta-1)*Xi+2*eta*G)/eta
        B=((1-eta)*Xi-1-3*eta*G)/eta
        UU=4*eta*(A*(special.j1(u)/u)**2+B*special.j0(u)*special.j1(u)/u+G*special.j1(2*u)/u)
        Sq=1/(1+UU)
    result=dA(np.r_[[q,Sq]])
    result.setColumnIndex(iey=None)
    result.packingfraction=eta
    result.R=R
    result.a=(np.pi*R**2/(eta*3/2.*3**0.5))**0.5
    result.modelname=inspect.currentframe().f_code.co_name
    return result


def PercusYevick1D(q,R=1,eta=0.1):
    """
    The PercusYevick structure factor in 1D

    Structure factor for the potential U(r)= (inf for 0<r<R) and (0 for R<r).

    Parameters
    ----------
    q : array; N dim
        scattering vector; units 1/(R[unit])
    R : float
        Radius of the object
    eta : float
        packing fraction as eta=2*R*n  with number density n

    Returns
    -------
    dataArray 
    [q,structure factor]

    Notes
    -----
    .. [1] Exact solution of the Percus-Yevick equation for a hard-core fluid in odd dimensions
           Leutheusser E  Physica A 1984 vol: 127 (3) pp: 667-676
    .. [2] On the equivalence of the Ornstein–Zernike relation and Baxter’s relations for a one-dimensional simple fluid
           Chen M Journal of Mathematical Physics 1975 vol: 16 (5) pp: 1150 

    """
    q=np.atleast_1d(q)
    D=2.*R
    nn=eta/D
    if R==0 or eta==0:
        Sq=np.ones_like(q)
    else:
        # exchange q=zero with small Q as limit
        Q=np.piecewise(q,[q==0],[1e-8,lambda q: q])
        xi=(1-D*nn)
        cQ=-2*(1./Q/xi*np.sin(Q*D) + nn/Q**2/xi**2*(1-np.cos(Q*D)))
        Sq=(1-cQ*nn)**-1  # =1/A eq 6 and 8b of [1]_
    result=dA(np.r_[[q,Sq]])
    result.setColumnIndex(iey=None)
    result.packingfraction=eta
    result.R=R
    result.nkTkappa=xi**2
    result.modelname=inspect.currentframe().f_code.co_name
    return result


def stickyHardSphere(q,R,width,depth,molarity=None,phi=None):
    """
    Structure factor of a square well potential with depth and width (sticky hard spheres).
    
    Sticky hard sphere model is derived using a perturbative solution of the factorized
    form of the Ornstein-Zernike equation and the Percus-Yevick closure relation.
    The perturbation parameter is width/(width+2R)
    
    Parameters
    ----------
    q : array; N dim
        Scattering vector; units 1/(R[unit])
    R : float
        Radius of the hard sphere
    phi : float
        Volume fraction of the hard core particles
    molarity : float
        Number density in mol/l and defines q and R units to 1/nm and nm to be correct
        Preferred over phi if both given.
    depth : float
        Potential well depth in kT
        depth >0 (U<0); positive potential allowed (repulsive) see [1]_.
    width : float
        Width of the square well
        
    Notes
    -----
    | The potential U(r) is defined as
    | r<2R             U(r)=infinity
    | 2R<r<2R+width    U(r)=-depth   in [kT]
    | r >2R+width      U(r)=0
    
    eps=width/(2*R+width) 
    stickyness=exp(-depth)/12./eps
    
    References
    ---------- 
    .. [1] S.V. G. Menon, C. Manohar, and K. S. Rao, J. Chem. Phys. 95, 9186 (1991)
    .. [2] M. Sztucki, T. Narayanan, G. Belina, A. Moussaïd, F. Pignon, and H. Hoekstra, Phys. Rev. E 74, 051504 (2006)
    .. [3] W.-R. Chen, S.-H. Chen, and F. Mallamace, Phys. Rev. E 66, 021403 (2002)
    .. [4] G. Foffi, E. Zaccarelli, F. Sciortino, P. Tartaglia, and K. A. Dawson, J. Stat. Phys. 100, 363 (2000)

    """
    # get volume fraction eta from number density and radius R
    if isinstance(molarity,(float,int)):
        numdens=constants.N_A*molarity*1e-24  # from mol/l to particles/nm**3
        phi=4/3.*np.pi*R**3*numdens
    elif isinstance(phi,(float,int)):
        numdens=phi/(4/3.*np.pi*R**3)
        molarity=numdens/(constants.N_A*1e-24)
    else:
        raise Exception('one of molarity/eta needs to be given.')

    # to prevent math range error in fits
    if depth<-200:depth=-200

    q=np.atleast_1d(q)
    Q=np.piecewise(q,[q==0],[1e-8,lambda q: q])  # avoid zero

    eps=width/(2*R+width)  # pertubation parameter
    tau=math.exp(-depth)/12./eps  # stickyness
    eta=phi*(1-eps)**3
    lam=(1+0.5*eta)/(1-eta)**2/(eta**2/(1-eta)-eta/12.+tau)
    mu=lam*eta*(1-eta)
    al=(1+2*eta-mu)/(1-eta)**2
    be=(-3*eta+mu)/2./(1-eta)**2
    k=Q*(2*R+width)

    sink=np.sin(k)
    cosk=np.cos(k)
    Ak=1+12*eta*(al*((sink-k*cosk)/k**3)+be*(1-cosk)/k**2-lam/12.*sink/k)
    Bk=12*eta*(al*(0.5/k-sink/k**2+(1-cosk)/k**3)+be*(1/k-sink/k**2)-lam/12.*((1-cosk)/k))
    Sk=1./(Ak*Ak+Bk*Bk)

    result=dA(np.r_[[q,Sk]])
    result.welldepth=depth
    result.weelwidth=width
    result.stickiness=tau
    result.volumefraction=phi
    result.eta=eta
    result.molarity=molarity
    result.modelname=inspect.currentframe().f_code.co_name
    return result


def adhesiveHardSphere(q,R,tau,delta,molarity=None,eta=None):
    """
    structure factor of a adhesive hard sphere potential (a square well potential)
    
        
    Parameters
    ----------
    q : array; N dim
        scattering vector; units 1/(R[unit])
    R : float
        radius of the hard core
    eta : float
        volume fraction of the hard core particles
    molarity : float
        number density in mol/l and defines q and R units to 1/nm and nm to be correct
        preferred over eta if both given
    tau : float
        stickiness
    delta : float
        width of the square well
        
    Notes
    -----
    The potential U(r) is defined as 
    r<2R             U(r)=infinity
    2R<r<2R+delta    U(r)=-depth=ln(12*tau*delta/(2R+delta))   
    r >2R+delta      U(r)=0
    
    
    References
    ---------- 
    .. [1] C. Regnaut and J. C. Ravey, J. Chem. Phys. 91, 1211 (1989).
    .. [2] C. Regnaut and J. C. Ravey, J. Chem. Phys. 92 (5) (1990), 3250 Erratum
    
    """
    # get volume fraction eta from number density and radius R
    if isinstance(molarity,(float,int)):
        numdens=constants.N_A*molarity*1e-24  # from mol/l to particles/nm**3
        eta=4/3.*np.pi*R**3*numdens
    elif isinstance(eta,(float,int)):
        numdens=eta/(4/3.*np.pi*R**3)
        molarity=numdens/(constants.N_A*1e-24)
    else:
        raise Exception('one of molarity/eta needs to be given.')
    q=np.atleast_1d(q)

    sigma=2.*R+delta
    k=np.piecewise(q,[q==0],[1e-8,lambda q: q*sigma])
    phi=eta*(sigma/(2*R))**3

    lam=6.*(tau/phi+1.0/(1.-phi))
    try:
        lam1=lam+math.sqrt(lam**2-12./phi*(1.+0.5*phi)/(1-phi)**2)
        lam2=lam-math.sqrt(lam**2-12./phi*(1.+0.5*phi)/(1-phi)**2)
        lambd=lam1 if abs(lam1)<abs(lam2) else lam2
    except ValueError:  # complex root
        return -1

    mu=lambd*phi*(1.-phi)
    A=0.5*(1.+2.*phi-mu)/(1.-phi)**2
    B=0.5*sigma*(mu-3.*phi)/(1.-phi)**2
    C=-A*sigma**2-B*sigma+lambd*sigma**2/12.

    sink=np.sin(k)
    cosk=np.cos(k)
    I0=sink/k
    I1=(cosk+k*sink-1.0)/k**2
    I2=(k**2*sink-2.0*sink+2.0*k*cosk)/k**3
    J0=(1-cosk)/k
    J1=(sink-k*cosk)/k**2
    J2=(2.*sink*k+2.*cosk-k**2*cosk-2.)/k**3

    alpha=1.0-12.0*phi*(C/sigma**2*I0+B/sigma*I1+A*I2)
    beta=12.0*phi*(C/sigma**2*J0+B/sigma*J1+A*J2)

    SQ=1./(alpha*alpha+beta*beta)

    result=dA(np.r_[[q,SQ]])
    try:
        result.welldepth=math.log(12*tau*delta/sigma)
    except:
        result.welldepth=-np.inf
    result.wellwidth=delta
    result.stickiness=tau
    result.welldepth=math.log(12*tau*delta/sigma) if 12*tau*delta/sigma>0 else np.inf
    result.HSvolumefraction=eta
    result.phi=phi
    result.modelname=inspect.currentframe().f_code.co_name
    return result


def criticalSystem(q,corrlength,isothermalcompress):
    """
    structure factor of a critical system should take the Ornstein-Zernike form 
    
    Parameters
    ----------
    q : array; N dim
        scattering vector; units 1/(R[unit])
    corrlength : float
        correlation length
    isothermalcompress : float
        isothermal compressibility of the system

    Notes
    -----
    The peaking of the structure factor near Q=0 region is due to attractive interaction.
    Away from it the structure factor should be close to the hard sphere structure factor.
    Near the critical point we should find 
    S(Q)=S_PY(Q)+S_OZ(Q)
    S_PY Percus Yevik structure factor
    S_OZ this function
    
    References
    ----------
    .. [1] Analysis of Critical Scattering Data from AOT/D2O/n-Decane Microemulsions
           S. H. Chen, T. L. Lin, M. Kotlarchyk
           Surfactants in Solution pp 1315-1330
    
    """
    Q=np.atleast_1d(q)
    result=dA(np.r_[[Q,isothermalcompress/(1+Q**2*corrlength**2)]])
    result.corrlength=corrlength
    result.isothermalcompress=isothermalcompress
    result.modelname=inspect.currentframe().f_code.co_name
    return result


#------------------------------------------------------------------
# hydrodynamic function
#see Beenakker ref 2 Table 1, given is phi*gamma0^m/n
_tablegamma0='0.0 0.0 0.0 0.0 0.0 \
              0.05 0.0553 0.0542 0.0533 0.0525 0.10 0.1228 0.1177 0.1135 0.1104 0.15 0.2048 0.1918 0.1813 0.1738  \
              0.20 0.3038 0.2777 0.2574 0.2432 0.25 0.4224 0.3766 0.3423 0.3186 0.30 0.5627 0.4895 0.4364 0.4005  \
              0.35 0.7267 0.6172 0.5402 0.4888 0.40 0.9157 0.7601 0.6538 0.5839 0.45 1.1310 0.9183 0.7776 0.6856'
_gamma0=np.fromstring(_tablegamma0,sep=' ').reshape(-1,5).T
#interpolate polynom order 3
_gamma0poly=np.polyfit(_gamma0[0],_gamma0[1:].T,4)      #about 200µs
#calc values as np.polyval(_gamma0poly,xx)

def _Sg(xx,mm1):
    """
    from Genz [1] equ 6 with gamma0 from [2]_ Table 1
    Sg=C(x) + .......
    this is for all ak (see Beenakker ref 2 ) and accurate in (volume fraction)**2
    returns array
    """
    x=np.where(xx==0,np.ones_like(xx)*1e-5,xx)  # avoid zero
    x2=2*x
    x3=x*x*x
    x4=x3*x
    cxx=9/2.*(special.sici(x2)[0]/x+ 0.5*np.cos(x2)/x/x+ 0.25*np.sin(x2)/x3-
                np.sin(x)**2/x4- 4/x3/x3*(np.sin(x)-x*np.cos(x))**2)
    Cx=np.where(xx==0,np.ones_like(xx)*2.5,cxx)  # zero is equal 2.5
    func=( Cx + 9./4 * np.pi *5/9.*   mm1[0] * 9./x3 * special.jn(1.5, x) ** 2 +
                9./4 * np.pi * 1. *   mm1[1] *25./x3 * special.jn(2.5, x) ** 2 +
                9./4 * np.pi * 1. *   mm1[2] *49./x3 * special.jn(3.5, x) ** 2 +
                9./4 * np.pi * 1. *   mm1[3] *81./x3 * special.jn(4.5, x) ** 2 )
    return func


def _HINTEGRAL(Q,Rh,molarity,sffunc,sfargs={},numberOfPoints=50):
    """
    calculation of hydrodynamic function for one Q
    see hydrodynamicFunct
    """
    # set to zero to get debug messages; debuglevel>10 no messages
    debuglevel=10
    phi=4/3*np.pi*Rh**3*constants.N_A*molarity*1e-24
    if phi>0.5 :
        print('to large volume fraction %.3g in H' %(phi))
        return -1
    # coefficients for the gamma0^m/n
    mm1=np.polyval(_gamma0poly,phi)/phi-1

    def Sq(q):
        """structure factor; infinite S(Q=inf)=1            """
        # ravel q
        sf=sffunc(q.ravel(),**sfargs)
        # reshape sf to q shape
        if sf._isdataArray: return sf.Y.reshape(q.shape)
        return sf.reshape(q.shape)

    ak=np.r_[0:np.pi*3:numberOfPoints*3j,np.pi*2:np.pi*53:numberOfPoints*4j]
    k=ak/Rh
    x= np.cos(np.r_[np.pi:0:-numberOfPoints*2j])   # x is cos(angle(k,k`))

    Qmk=np.sqrt(Q**2+k**2-2*Q*k*x[:,None])
    #(Sq(Qmk)-1) is correct as compared with [2]_ equ 5.7 and 5.9
    integrand=np.sinc(ak/np.pi)**2/(1+phi*_Sg(ak,mm1))*(1-x[:,None]**2)*(Sq(Qmk)-1)
    integrandak=np.trapz(integrand,x=x,axis=0)
    integral=np.trapz(integrandak,x=ak,axis=0)
    return np.r_[Q,3./2./np.pi*integral]


def _HINTEGRALDs(Rh,molarity,numberOfPoints=50):
    """
    calculation of hydrodynamic function for the self diffusion Ds
    see hydrodynamicFunct
    number of points is number of points in integration in a pi interval
    """
    # set to zero to get debug messages; debuglevel>10 no messages
    debuglevel=10
    phi=4./3*np.pi*Rh**3*constants.N_A*molarity*1e-24
    if phi>0.5 :
        print('to large volume fraction %.3g in Ds' %(phi))
        return -1
    # coefficients for the gamma0^m/n
    mm1=np.polyval(_gamma0poly,phi)/phi-1
    ak=np.r_[0:np.pi*3:numberOfPoints*3j,np.pi*3:np.pi*153:numberOfPoints*50j]
    integrandDs=np.sinc(ak/np.pi)**2/(1+phi*_Sg(ak,mm1))
    integralDs=np.trapz(integrandDs,x=ak)
    return 2/np.pi*integralDs


def hydrodynamicFunct(wavevector,Rh,molarity,intrinsicVisc=None,DsoverD0=None,
                      structureFactor=None,structureFactorArgs={},
                      numberOfPoints=50,ncpu=-1):
    """
    Hydrodynamic function H(Q) from hydrodynamic pair interaction of spheres in suspension.

    We use the theory from Beenakker and Mazur [2]_ as given by Genz [1]_.
    The :math:`\delta\gamma`-expansion of Beenakker expresses many body hydrodynamic 
    interaction within the renormalization approach dependent on the structure factor S(q).

    Parameters
    ----------
    wavevector : array
        scattering vector q in units 1/nm
    Rh : float
        effective hydrodynamic radius of particles in nm.
    molarity : float
        | molarity in mol/l
        | This overides a parameter 'molarity' in the structureFactorArgs.
        | Rh and molarity define the hydrodynamic interaction, the volume fraction and Ds/D0 for H(Q).
        | The structure factor may have a radius different from Rh e.g. for attenuated hydrodynamic interactions.
    DsoverD0 : float
        | The high Q limit of the hydrodynamic function is for low volume fractions
        | Ds/D0= 1/(1+intrinsicVisc * volumeFraction ) with self diffusion Ds.
        | Ds is calculated from molarity and Rh.
        | This explicit value overrides intrinsic viscosity and calculated Ds/D0.
    structureFactor : function, None
        |  Structure factor S(q) with S(q=inf)=1.0 recommended.
        |  1: If structurefactor is None a Percus-Yevik is assumed with molarity and R=Rh.
        |  2: A function S(q,...) is given as structure factor, which might be an
        |     empirical function (e.g. polynominal fit of a measurement)
        |     First parameter needs to be wavevector q .
        |     If "molarity" parameter is present it is overwriten by molarity above.
    structureFactorArgs : dictionary
        Any extra arguments to structureFactor e.g. structFactorArgs={'x':0.123,R=3,....}
    intrinsicVisc : float
        | Defines the high q limit for the hydrodynamic function.
        | effective_viscosity= eta_solvent * (1-intrinsicVisc*Volumefraction )
        | intrinsicVisc = 2.5 Einstein hard sphere density 1 g/cm**3
        | For proteins instead of volume fraction  the protein concentration in g/ml with typical
        | protein density 1.37 g/cm^3 is often used.
        | Intrinsic Viscosity depends on protein shape (see HYDROPRO).
        | Typical real values for intrinsicVisc in practical units cm^3/g
        |   sphere 1.76 cm^3/g= 2.5    sphere with protein density
        |   ADH    3.9        = 5.5    a tetrameric protein
        |   PGK    4.0        = 5.68   two domains with hinge-> elongated
        |   Rnase  3.2        = 4.54   one domain
        | eta_solvent/effective_viscosity = (1-intrinsicVisc * Volumefraction )=Dself/D0
    numberOfPoints : integer, default 50
        Determines number of integration points in equ 5 of ref [1]_ and therfore accuracy of integration.
        The typical accuracy of this function is <1e-4 for (H(q) -highQLimit) and <1e-3 for Ds/D0.

    Returns
    -------
    dataArray 
        | [0] q values
        | [1] hydrodynamic function
        | [2] hydrodynamic function only Q dependent part = H(q) -highQLimit
        | [3] structure factor for H(q) calculation
        | .selfdiffusion Ds

    Notes
    -----
    Ds is calculated according to equ 11 in [1]_ which is valid for volume fractions up to 0.5.
    With this assumption the deviation of self diffusion Ds from 
    Ds=Do*[1-1.73*phi+0.88*phi**2+ O(phi**3)] is smaller 5% for phi<0.2 (10% for phi<0.3)

    References
    ----------
    .. [1] U. Genz and R. Klein, Phys. A Stat. Mech. Its Appl. 171, 26 (1991).
    .. [2] C. W. J. Beenakker and P. Mazur, Phys. A Stat. Mech. Its Appl. 126, 349 (1984).
    .. [3] C. W. J. Beenakker and P. Mazur, Phys. A Stat. Mech. Its Appl. 120, 388 (1983).
    
    
    """
    # set to zero to get debug messages; debuglevel>10 no messages
    debuglevel=0
    if structureFactor==None:
        # we use PercusYevic Structure factor --> hard spheres
        structureFactor=PercusYevick
        if 'R' not in structureFactorArgs:
            structureFactorArgs={'R':Rh}
    sfcode=formel._getFuncCode(structureFactor)
    if 'molarity' in structureFactorArgs or \
       'molarity' in  sfcode.co_varnames[:sfcode.co_argcount] :
        # the last examines the function
        # overwrite or append 'molarity'
        structureFactorArgs=dict(structureFactorArgs, **{'molarity':molarity})
    if debug>debuglevel:
        p=grace()
        XX=np.r_[min(wavevector)/10.:max(wavevector)*2:100j]
        p.plot(structureFactor(XX,**structureFactorArgs),line=1,symbol=0)
        p.plot(structureFactor(wavevector,**structureFactorArgs))
    # Volume fraction
    phi=lambda mol,R: 4/3.*np.pi*R**3*constants.N_A*mol/(10e7)**3
    if phi(molarity,Rh)>0.5:
        raise ValueError('Volume fraction %.3g to high; Chose appropriate Rh or molarity for Volume fraction <0.5' %phi(molarity,Rh))
    res=[]
    qqq=np.atleast_1d(wavevector)
    columnname=['q','HydDynFun','HydDynfun-DsoverD0','structureFactor']

    if debug>debuglevel:
        print(columnname[:-1])
        def cb(res):  # for intermediate results
            print(res[0],1+res[1],(0+res[1]))
    else:
        cb=None

    Ds=_HINTEGRALDs(Rh=Rh,molarity=molarity,numberOfPoints=numberOfPoints)
    if DsoverD0!=None:
        Hinf=DsoverD0
    elif intrinsicVisc!=None:
        DsintrVisc=1/(1+intrinsicVisc*phi(molarity,Rh))
        Hinf=DsintrVisc
        DsoverD0=DsintrVisc
    else:
        Hinf=Ds
        DsoverD0=Ds

    # in parallel for production run
    # if debug!= None it will be single thread
    res=parallel.doForQlist(_HINTEGRAL,
                            qqq,
                            Rh=Rh,
                            molarity=molarity,
                            sffunc=structureFactor,
                            sfargs=structureFactorArgs,
                            numberOfPoints=numberOfPoints,
                            ncpu=ncpu,
                            cb=cb,)
    # and calc final result from this
    result=dA(np.c_[qqq,
                    Hinf+np.array(res)[:,1],
                    np.array(res)[:,1],
                    structureFactor(wavevector,**structureFactorArgs).Y].T)
    if debug>debuglevel:
        p.plot(result)
    result.Sq=structureFactor
    result.SqArgs=str(structureFactorArgs)
    result.Rh=Rh
    result.molarity=molarity
    result.intrinsicVisc=intrinsicVisc
    result.phi_Rh=phi(molarity,Rh)
    result.DsoverD0=DsoverD0
    result.numberOfPoints=numberOfPoints
    result.columnname=columnname
    result.setColumnIndex(iey=None)
    return result



