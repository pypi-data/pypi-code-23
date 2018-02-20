from __future__ import print_function

import numpy as np
import scipy as sp
import warnings


#--------------------------------------------------
def lambda_iak(rho, alpha, beta, E0=200.0):
    '''
    Compute inelastic mean free scattering length of electron through 
    material with specific gravity rho using Iakabouvskii's method 
    from 2008, as documented in p298 of Egerton.
    
    Returns inelastic mean free path length.
    
    Parameters
    ----------
    rho : scalar
        specific gravity in g/cm^3.
    alpha : scalar
        convergence semi-angle in mrad.
    beta : scalar
        collect semi-anfle in mrad.
    E0 : scalar, optional
        Accelerating voltage in keV.
   
    Returns
    -------
    lambda : scalar
        Inelastic mean free path length.
    
    '''
    
    F = (1.0+E0/1022.0) / (1+E0/511.0)**2
    d2 = np.abs(alpha**2 - beta**2)
    tc = 20.0
    te = 5.5*rho**0.3/(F*E0)
    a2 = alpha**2
    b2 = beta**2
    
    lnarg = (a2+b2+d2+2.0*te**2) / (a2+b2+d2+2.0*tc**2) * tc**2/te**2
    lam = 200.0*F*E0/(11.0*rho**0.3) / np.log(lnarg)

    return lam 


#--------------------------------------------------
def lambda_nm_rel(kV=200.0):
    '''
    Compute relativistic wavelength of electron at acceleration 
    voltage kV, in kilovolts.
    
    Returns wavelength in nm.
    '''
    
    warnings.warn(
        "'lambda_nm_rel' is depricated. Use 'e_lambda' instead.",
        DeprecationWarning
    )
    
    h = sp.constants.h
    m = sp.constants.m_e
    e = sp.constants.e
    c = sp.constants.c
    lam = h/np.sqrt(2.0*m*e*kV*1000.0*(1+e*kV*1000.0/(2.0*m*c**2)))*1e9
    
    return lam


#--------------------------------------------------
def e_lambda(V=200e3, rel=True):
    '''
    Compute wavelength of electron at acceleration voltage V.
    
    Returns wavelength in metres. 
    
    Parameters
    ----------
    rel : bool, optional
        If True, use relativistic calculation, else use classical.
    
    Returns
    -------
    Wavetlength : scalar
        Electron wavelength in meters.
    
    '''
    
    me = sp.constants.m_e
    h = sp.constants.h
    e = sp.constants.e
    c = sp.constants.c
        
    if rel:
        lam = h/np.sqrt(2*me*e*V*(1+e*V/(2*me*c**2)))
    else:
        lam = h/np.sqrt(2*me*e*V)
    return lam


#--------------------------------------------------
def d_recip_nm_from_two_theta_mrad(two_theta, kV=200.0):
    '''
    Compute d-spacing from deflection angle of electron accelerated 
    through voltage kV in kilovolts.
    
    Returns d-spacing in reciprocal nm.
    
    Parameters
    ----------
    two_theta : scalar
        Deflection in mrad, the angle to the undeflected spot.
    kV : scalar, optional
        Electron accelerating voltage in kilovolts.
    
    Returns
    -------
    Returns d-spacing in reciprocal nm.
    
    '''
    
    theta = np.asarray(two_theta, float)/2.0/1000
    #lam = lambda_nm_rel(kV=kV)
    lam = e_lambda(V=kV*1000, rel=True)
    d = lam/(2.0*np.sin(theta))
    
    return 1.0/d


#--------------------------------------------------
def hkl_cube(alpha, n=10, V=200e3, struct='fcc'):
    '''
    Compute diffraction parameters for a cubic lattice.
    
    Returns unique hkl values, d-spacing and deflection angles.
    
    Parameters
    ----------
    alpha : scalar
        Cube edge length in meters.
    n : integer, optional
        Number of values of each hkl to consider.
    V : scalar, optional
        Electron accelerating voltage in volts.
    struct : string, optional
        String controlling structure of cell.
        Only 'fcc' is currently understood.
    
    Returns
    -------
    Tuple of sorted hkl of unique d-spacing, d-spacing and mrad 
    deflection from the direct (undeviated) spot.
    
    '''
    
    hkl = np.asarray(list(itertools.product(list(range(n)),
                                            list(range(n)), 
                                            list(range(n)))))[1:,:]

    if struct == 'fcc':
        # fcc H,K,L all odd or all even
        n_odd = (hkl & 0x1).sum(-1)    # number of odd
        fcc_i = np.where(np.logical_or(n_odd == 3, n_odd == 0))[0]
        hkl = hkl[fcc_i, :]          # allowed
    else:
        print("Struct not supported, returning all reflections.")
        
    hkl2 = (hkl**2).sum(-1)     # sumsq
    hkl2_si = np.argsort(hkl2)  # index of increasing size
    hkl2s = hkl2[hkl2_si]       # sorted sumsq
    hkls = hkl[hkl2_si, :]      # sorted hkl
    hkl2s_u, hkl2s_i = np.unique(hkl2s, return_index=True)
    
    # unique reflection spacing
    d = alpha/hkl2s_u**0.5                  
    # e wavelength nm
    elam_nm = e_lambda(V=V, rel=True)*1e9           
    # mrad of angle from undeviated
    bragg_2t_mrad = 2*np.arcsin(elam_nm/(2*d))*1000
    
    return (hkls[hkl2s_i], d, bragg_2t_mrad)

