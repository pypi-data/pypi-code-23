# encoding: utf-8
#
#Copyright (C) 2017, P. R. Wiecha
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
"""
Collection of incident fields
"""

import itertools

import numpy as np

from pyGDMfor import elecmag0_full as forelecmag0_full
from pyGDMfor import magmag0_full as formagmag0_full
from pyGDMfor import evanescentfield as forevanescentfield






#==============================================================================
# Incident field container class
#==============================================================================
class efield(object):
    """incident electromagnetic field container class
    
    Defines an incident electric field including information about wavelengths,
    polarizations, focal spot or whatever optional parameter is supported by
    the used field generator.
    
    Parameters
    ----------
    field_generator : `callable`
        field generator function. Mandatory arguments are 
         - `struct` (instance of :class:`.structures.struct`)
         - `wavelength` (list of wavelengths)
    
    wavelengths : list
        list of wavelengths (wavelengths in nm)
    
    kwargs : list of dict or dict
        possible additional keyword arguments, passed to `field_generator`.
        Either dict or list of dicts.
         - If list of dicts, each entry must correspond exactly to one 
           parameters-set for `field-generator`.
         - If dict, maybe contain lists for configurations of the parameters. 
           In that case, all possible parameter-permutations will be generated.
    
    Examples
    --------
    >>> kwargs = dict(theta = [0.0,45,90])
    [{'theta': 0.0}, {'theta': 45.0}, {'theta': 90.0}]
    
    is equivalent to:
    
    >>> kwargs = [dict(theta=0.0), dict(theta=45.0), dict(theta=90.0)]
    [{'theta': 0.0}, {'theta': 45.0}, {'theta': 90.0}]
    
    """
    def __init__(self, field_generator, wavelengths, kwargs):
        """initialize field container"""
        self.field_generator = field_generator
        self.wavelengths = wavelengths
        self.kwargs = kwargs
        
        ## --- generate parameter-sets for field-generator
        if type(kwargs) == dict:
            ## --- integer parameters to list
            for key in kwargs:
                if type(kwargs[key]) not in [list, np.ndarray]:
                    kwargs[key] = [kwargs[key]]
            
            ## --- generate all permutations of kwargs for direct use in field_generator
            varNames = sorted(kwargs)
            self.kwargs_permutations = [dict(zip(varNames, prod)) for 
                                    prod in itertools.product(*(kwargs[varName] 
                                                for varName in varNames))]
        elif type(kwargs) == list:
            self.kwargs_permutations = []
            for kw in kwargs:
                self.kwargs_permutations.append(kw)
                if type(kw) != dict:
                    raise ValueError("Wrong input for 'kwargs': Must be either dict or list of dicts.")
                
        else:
            raise ValueError("Wrong input for 'kwargs': Must be either dict or list of dicts.")
        
        
        self.dtypef = None
        self.dtypec = None
    
    
    def setDtype(self, dtypef, dtypec):
        """set dtype of arrays"""
        self.dtypef = dtypef
        self.dtypec = dtypec
        self.wavelengths = np.asfortranarray(self.wavelengths, dtype=dtypef)










        

#==============================================================================
# Electric field generator functions
#==============================================================================




#def null(simDict, Ilambda=1, Itheta=1, returnField='E'):
#    """Zero-Field
#    
#    Parameters
#    ----------
#      simDict : dict 
#          generated from 'genSimDict'
#      Ilambda, Itheta : int, optional (default=1)
#          Nr of Wavelength/Polarization (index starting at 1!)
#      returnField : str, default: 'E'
#          if 'E': returns electric field; if 'B': magnetic field
#    
#    Returns:
#    ----------
#      E0:       Complex zero at each dipole position
#    """
#    xm = simDict['xm']
#    ym = simDict['ym']
#    zm = simDict['zm']
#    cn1 = complex(simDict['n1'], 0)
#    cn2 = complex(simDict['n2'], 0)
#    cn3 = complex(simDict['n3'], 0)
#    
#    if type(xm) in [np.float32, np.complex64]:
#        DTYPE='c8'
#    else:
#        DTYPE='c16'
#    
#    Ex = np.zeros(len(xm), dtype=DTYPE)
#    Ey = np.zeros(len(ym), dtype=DTYPE)
#    Ez = np.zeros(len(zm), dtype=DTYPE)
#    
#    Evec = np.array([Ex, Ey, Ez]).T.flatten()
#    return np.asfortranarray(Evec)




##----------------------------------------------------------------------
##                      INCIDENT FIELDS
##----------------------------------------------------------------------
def planewave(struct, wavelength, theta, kSign=-1, 
                      consider_substrate_reflection=False, returnField='E'):
    """Normally incident (along Z) planewave
    
    Amplitude = 1 for both, E and B 
    
    Parameters
    ----------
    struct : :class:`.structures.struct`
        structure definition, including environment setup
    
    wavelength : float
        Wavelength in nm
    
    theta : float
        polarization angle in degrees, 0deg = 0X direction
    
    kSign : int, default: -1
        sign of wavenumber. 
        +1: propagation from bottom to top (towards increasing z)
        -1: propagation from top to bottom (towards smaller z, default)
          
    consider_substrate_reflection : bool, default: False
        Whether to consider the reflection / transmission coefficient at the
        substrate for adjusting the field amplitude
    
    returnField : str, default: 'E'
        if 'E': returns electric field; if 'B': magnetic field
    
    Returns
    -------
      E0 (B0):       Complex E-(B-)Field at each dipole position as 
                     list of (complex) 3-tuples: [(Ex1, Ey1, Ez1), ...]
    """
    xm, ym, zm = np.transpose(struct.geometry)
    cn1 = struct.n1
    cn2 = struct.n2
    cn3 = struct.n3
    
    ## --- reflection and transmission coefficients
    if kSign == 1:
        t01 = 2.*cn1 / (cn1+cn2)
        r01 = (cn1-cn2) / (cn1+cn2)
    elif kSign == -1:
        t01 = 2.*cn2 / (cn1+cn2)
        r01 = (cn2-cn1) / (cn1+cn2)
    else:
        raise ValueError("planewave: kSign must be either +1 or -1!")
    
    ## constant parameters
    E0 = B0 = complex(1,0)
    kx = complex(0,0)
    ky = complex(0,0)
    kz = kSign*cn2 * (2*np.pi / wavelength)    #incidence from positive Z
    
    ## phase in zone "2"
    cphase2 = np.exp(1j * (kx*xm + ky*ym + kz*zm) )
    
    ## amplitude and polarization
    ##  --------- Electric field --------- 
    if returnField in ['e', 'E']:
        Ex = E0 * np.cos(theta * np.pi/180.)*cphase2
        Ey = E0 * np.sin(theta * np.pi/180.)*cphase2
        Ez = np.zeros(len(zm))
    ##  --------- Magnetic field --------- 
    else:
        Ex = -B0 * np.sin(theta * np.pi/180.)*cphase2
        Ey = B0 * np.cos(theta * np.pi/180.)*cphase2
        Ez = np.zeros(len(zm))
    
    if consider_substrate_reflection:
        if kSign == 1:  # bottom to top
            Ex[zm>0] *= t01
            Ey[zm>0] *= t01
            Ex[zm<=0] += r01*E0 * np.cos(theta * np.pi/180.)*cphase2[zm<=0]
            Ey[zm<=0] += r01*E0 * np.sin(theta * np.pi/180.)*cphase2[zm<=0]
        else:           # top to bottom
            Ex[zm<=0] *= t01
            Ey[zm<=0] *= t01
            Ex[zm>0] += r01*E0 * np.cos(theta * np.pi/180.)*cphase2[zm>0]
            Ey[zm>0] += r01*E0 * np.sin(theta * np.pi/180.)*cphase2[zm>0]
    
    Evec = np.transpose([Ex, Ey, Ez])
    return np.asfortranarray(Evec, dtype=struct.dtypec)
    

    
def evanescent_planewave(struct, wavelength, theta_inc=0, polar='s',
                         returnField='E'):
    """oblique incident planewave
    
    Oblique incidence (from bottom to top) through n1/n2/n3 layer interfaces. 
    May be used to simulate evanescent fields in the total internal 
    reflection configuration.
    Amplitude = 1 for both, E and B.
    
    Parameters
    ----------
    struct : :class:`.structures.struct`
        structure definition, including environment setup
    
    wavelength : float
        Wavelength in nm
    
    theta_inc : float, default: 0
        incident angle in the XZ plane with respect to e_z, in degrees.
         - 0deg = along Z (form neg to pos Z)
         - 90deg = along X  (form pos to neg X)
    
    polar : str, default: 's'
        incident polarization. Either 's' or 'p'. 
        At 0 degree incident angle, 's' is polarized along x, 'p' along y.
    
    returnField : str, default: 'E'
        if 'E': returns electric field; if 'B': magnetic field
    
    Returns
    -------
      E0 (B0):       Complex E-(B-)Field at each dipole position as 
                     list of (complex) 3-tuples: [(Ex1, Ey1, Ez1), ...]
    """
    
    spacing = struct.spacing
    xm, ym, zm = np.transpose(struct.geometry)
    posObj = np.transpose([xm,ym,zm])
    
    cn1 = struct.n1
    cn2 = struct.n2
    cn3 = struct.n3
    
    if polar == 's':
        idx_pol = 0
    elif polar == 'p':
        idx_pol = 1
    else:
        raise ValueError("'polar' must be either 's' or 'p'.")
    
    Ex = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ey = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ez = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    
    for i,R in enumerate(posObj):
        x,y,z = R
        ex,ey,ez, bx,by,bz = forevanescentfield(wavelength, theta_inc, spacing, 
                                                x,y,z, cn1,cn2,cn3)
        
        if returnField.lower() == 'e':
            Ex[i], Ey[i], Ez[i] = ex[idx_pol], ey[idx_pol], ez[idx_pol]
        else:
            Ex[i], Ey[i], Ez[i] = bx[idx_pol], by[idx_pol], bz[idx_pol]
        
    Evec = np.transpose([Ex, Ey, Ez])
    return np.asfortranarray(Evec, dtype=struct.dtypec)
    
    
    
def focused_planewave(struct, wavelength, theta, xSpot, ySpot, 
                      NA=-1, spotsize=-1, kSign=-1, 
                      consider_substrate_reflection=False, returnField='E'):
    """Normally incident (along Z) planewave with gaussian intensity profile
    
    Maximum amplitude = 1 for both, E and B, focused at (x0,y0)
    
    Parameters
    ----------
    struct : :class:`.structures.struct`
        structure definition, including environment setup
    
    wavelength : float
        Wavelength in nm
    
    theta : float
        polarization angle in degrees, 0deg = 0X direction
    
    kSign : int, default: -1
        sign of wavenumber. 
        +1: propagation from bottom to top (towards increasing z)
        -1: propagation from top to bottom (towards smaller z, default)
          
    consider_substrate_reflection : bool, default: False
        Whether to consider the reflection / transmission coefficient at the
        substrate for adjusting the field amplitude
        
    returnField : str, default: 'E'
        if 'E': returns electric field; if 'B': magnetic field
    
    Returns
    -------
      E0 (B0):       Complex E-(B-)Field at each dipole position as 
                     list of (complex) 3-tuples: [(Ex1, Ey1, Ez1), ...]
    """
    xm, ym, zm = np.transpose(struct.geometry)
    cn1 = struct.n1
    cn2 = struct.n2
    cn3 = struct.n3
    
    ## beamwaist
    if spotsize == NA == -1:
        raise ValueError("Focused Beam Error! Either spotsize or NA must be given.")
    elif spotsize == -1:
        w0 = 2*wavelength/(NA*np.pi)
    else:
        w0 = spotsize
    
    ## --- reflection and transmission coefficients
    if kSign == 1:
        t01 = 2.*cn1 / (cn1+cn2)
        r01 = (cn1-cn2) / (cn1+cn2)
    elif kSign == -1:
        t01 = 2.*cn2 / (cn1+cn2)
        r01 = (cn2-cn1) / (cn1+cn2)
    else:
        raise ValueError("Focused planewave: kSign must be either +1 or -1!")
    
    ## constant parameters
    E0 = B0 = complex(1,0)
    kx = complex(0,0)
    ky = complex(0,0)
    kz = kSign*cn2 * (2*np.pi / wavelength)    #incidence from positive Z
    
    ## phase in zone "2"
    cphase2 = np.exp(1j * (kx*xm + ky*ym + kz*zm) )
    I_gaussian =  np.exp( -1.0 * (((xm-xSpot)**2 + (ym-ySpot)**2) / (w0**2)))
    
    ## amplitude and polarization
    ##  --------- Electric field --------- 
    if returnField in ['e', 'E']:
        Ex = E0 * np.cos(theta * np.pi/180.)*cphase2*I_gaussian
        Ey = E0 * np.sin(theta * np.pi/180.)*cphase2*I_gaussian
        Ez = np.zeros(len(zm))
    ##  --------- Magnetic field --------- 
    else:
        Ex = -B0 * np.sin(theta * np.pi/180.)*cphase2*I_gaussian
        Ey = B0 * np.cos(theta * np.pi/180.)*cphase2*I_gaussian
        Ez = np.zeros(len(zm))
    
    if consider_substrate_reflection:
        if kSign == 1:  # bottom to top
            Ex[zm>0] *= t01
            Ey[zm>0] *= t01
            Ex[zm<=0] += r01*E0 * np.cos(theta * np.pi/180.)*cphase2[zm<=0]*I_gaussian[zm<=0]
            Ey[zm<=0] += r01*E0 * np.sin(theta * np.pi/180.)*cphase2[zm<=0]*I_gaussian[zm<=0]
        else:           # top to bottom
            Ex[zm<=0] *= t01
            Ey[zm<=0] *= t01
            Ex[zm>0] += r01*E0 * np.cos(theta * np.pi/180.)*cphase2[zm>0]*I_gaussian[zm>0]
            Ey[zm>0] += r01*E0 * np.sin(theta * np.pi/180.)*cphase2[zm>0]*I_gaussian[zm>0]
    
    Evec = np.transpose([Ex, Ey, Ez])
    return np.asfortranarray(Evec, dtype=struct.dtypec)
    


def gaussian(struct, wavelength, theta, xSpot, ySpot, zSpot=0, NA=-1, 
             spotsize=-1, kSign=-1, paraxial=False, returnField='E'):
    """Normal incident (along Z) Gaussian Beam Field
    
    obligatory "einKwargs" are: 'xSpot', 'ySpot' and one of 'NA' or 'spotsize'
    
    Parameters
    ----------
      struct : :class:`.structures.struct`
          structure object including environment
      
      wavelength : float
          Wavelength in nm
    
      theta : float
          polarization angle in degrees, 0deg = 0X direction
    
      xSpot,ySpot,zSpot : float,float 
          x/y/z coordinates of focal point
      
      NA : float
          Numerical aperture to calculate beamwaist
      
      spotsize : float (optional)
          Gaussian beamwaist (overrides "NA")
      
      kSign : float, default: -1
          Direction of Beam. -1: top to Bottom, 1 Bottom to top
      
      paraxial : bool, default: False
          Use paraxial Gaussian beam: No longitudinal fields.
          If "False", longitudinal components are obtained using Maxwell 
          equation div(E)=0 as condition
      
      returnField : str, default: 'E'
          if 'E': returns electric field; if 'B': magnetic field
    
    Returns
    -------
      E0:       Complex E-Field at each dipole position
    """
    xm, ym, zm = np.transpose(struct.geometry)
    cn1 = struct.n1
    cn2 = struct.n2
    cn3 = struct.n3
    
    Ex = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ey = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ez = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
#    posObj = np.transpose([xm,ym,zm])
    
    ak0 = 2.*np.pi / wavelength
    
    
    ## beamwaist
    if spotsize == NA == -1:
        raise ValueError("Focused Beam Error! Either spotsize or NA must be given.")
    elif spotsize == -1:
        w0 = 2*wavelength/(NA*np.pi)
    else:
        w0 = spotsize
    
    ## waist, curvature and gouy-phase
    def w(z, zR, w0):
        return w0 * np.sqrt(1 + (z/zR)**2)
    
    def R(z, zR):
        return z*( 1 + (zR/z)**2 )
    
    def gouy(z, zR):
        return np.arctan2(z,zR)
    
    ## constant parameters
    E0 = complex(1,0)
    k = kSign*cn2 * (2*np.pi / wavelength)    #incidence from positive Z
    zR = np.pi*w0**2 / wavelength
    
    r2 = (xm-xSpot)**2+(ym-ySpot)**2
    z = zm-zSpot
    
    ## amplitude and polarization
    E = E0 * (w0/w(z,zR,w0) * 
            np.exp(-r2 / w(z,zR,w0)**2 ) * 
            np.exp(1j * (k*z + k*r2/(2*R(z,zR)) - gouy(z, zR)) ))
    
    if returnField in ['E','e']:
        Ex = E*np.cos(theta*np.pi/180.)
        Ey = E*np.sin(theta*np.pi/180.)
    else:
        Ex = -1.*E*np.sin(theta*np.pi/180.)
        Ey = E*np.cos(theta*np.pi/180.)
        
    
    ## obtained longitudinal component using condition div(E)==0
    if paraxial:
        Ez = np.zeros(len(E))   # <-- paraxial gaussian beam: No longitudinal E-component
    else:
        Ez = (-1j * 2 / (k * w(z,zR,w0)**2)) * \
                ((xm-xSpot) * Ex + (ym-ySpot) * Ey)
    
    Evec = np.transpose([Ex, Ey, Ez])
    return np.asfortranarray(Evec, dtype=struct.dtypec)



def dipole_electric(struct, wavelength, x0,y0,z0, mx,my,mz, returnField='E'):
    """field emitted by an electric dipole at (x0,y0,z0) with complex amplitude (mx,my,mz)
    
    obligatory kwargs are: wavelength, x0,y0,z0, mx,my,mz
    
    From:  G. S. Agarwal, Phys. Rev. A, 11, 230 (1975). (Eqs. 4.5/4.6)
    
    Parameters
    ----------
      struct : :class:`.structures.struct`
          structure object including environment
     
      wavelength : float
        Wavelength in nm
    
      x0,y0,z0 : float
          x/y/z coordinates of magnetic dipole position
          
      mx,my,mz : float
          x/y/z amplitude of mag. dipole vector
          
      returnField : str, default: 'E'
          if 'E': returns electric field; if 'B': magnetic field
    
    Returns
    -------
      E0:       Complex E-Field at each dipole position ( (Ex,Ey,Ez)-tuples )
    """
    xm, ym, zm = np.transpose(struct.geometry)
    cn1 = struct.n1
    cn2 = struct.n2
    cn3 = struct.n3
    
    Ex = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ey = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ez = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    posObj = np.transpose([xm,ym,zm])
    
    ak0 = 2.*np.pi / wavelength
    
    ## get propagator S0
    for i,R in enumerate(posObj):
        xObs = R[0]
        yObs = R[1]
        zObs = R[2]
        if returnField in ['E','e']:
            ## magmag = elecelec
            cxx,cxy,cxz,\
                cyx,cyy,cyz,\
                czx,czy,czz\
                = formagmag0_full(ak0,xObs,yObs,zObs,
                                       x0,y0,z0,
                                       cn1,cn2,cn3)
            Ex[i] = cxx*mx + cxy*my + cxz*mz
            Ey[i] = cyx*mx + cyy*my + cyz*mz
            Ez[i] = czx*mx + czy*my + czz*mz
        else:
            cxx,cxy,cxz,\
                cyx,cyy,cyz,\
                czx,czy,czz\
                = forelecmag0_full(ak0,xObs,yObs,zObs,
                                       x0,y0,z0,
                                       cn1,cn2,cn3)
            Ex[i] = -1*cxx*mx + -1*cxy*my + -1*cxz*mz
            Ey[i] = -1*cyx*mx + -1*cyy*my + -1*cyz*mz
            Ez[i] = -1*czx*mx + -1*czy*my + -1*czz*mz
    
    Evec = np.transpose([Ex, Ey, Ez])
    return np.asfortranarray(Evec, dtype=struct.dtypec)



def dipole_magnetic(struct, wavelength, x0,y0,z0, mx,my,mz, returnField='E'):
    """field emitted by a magnetic dipole at (x0,y0,z0) with complex amplitude (mx,my,mz)
    
    obligatory "einKwargs" are: wavelength, x0,y0,z0, mx,my,mz
    
    From:  G. S. Agarwal, Phys. Rev. A, 11, 230 (1975). (Eqs. 4.5/4.6)
    
    Parameters
    ----------
      struct : :class:`.structures.struct`
          structure object including environment
     
      wavelength : float
        Wavelength in nm
    
      x0,y0,z0 : float
          x/y/z coordinates of magnetic dipole position
          
      mx,my,mz : float
          x/y/z amplitude of mag. dipole vector
          
      returnField : str, default: 'E'
          if 'E': returns electric field; if 'B': magnetic field
    
    Returns
    -------
      E0:       Complex E-Field at each dipole position ( (Ex,Ey,Ez)-tuples )
      
    """
    xm, ym, zm = np.transpose(struct.geometry)
    cn1 = struct.n1
    cn2 = struct.n2
    cn3 = struct.n3
    
    Ex = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ey = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    Ez = np.asfortranarray( np.zeros(len(xm)), dtype=struct.dtypec)
    posObj = np.transpose([xm,ym,zm])
    
    ak0 = 2.*np.pi / wavelength
    
    ## get propagator S0
    for i,R in enumerate(posObj):
        xObs = R[0]
        yObs = R[1]
        zObs = R[2]
        if returnField in ['E','e']:
#            raise ValueError("E not implemented")
            cxx,cxy,cxz,\
                cyx,cyy,cyz,\
                czx,czy,czz\
                = forelecmag0_full(ak0,xObs,yObs,zObs,
                                       x0,y0,z0,
                                       cn1,cn2,cn3)
            Ex[i] = -1*cxx*mx + -1*cxy*my + -1*cxz*mz
            Ey[i] = -1*cyx*mx + -1*cyy*my + -1*cyz*mz
            Ez[i] = -1*czx*mx + -1*czy*my + -1*czz*mz
        else:
            cxx,cxy,cxz,\
                cyx,cyy,cyz,\
                czx,czy,czz\
                = formagmag0_full(ak0,xObs,yObs,zObs,
                                       x0,y0,z0,
                                       cn1,cn2,cn3)
            Ex[i] = cxx*mx + cxy*my + cxz*mz
            Ey[i] = cyx*mx + cyy*my + cyz*mz
            Ez[i] = czx*mx + czy*my + czz*mz
    
    
    Evec = np.transpose([Ex, Ey, Ez])
    return np.asfortranarray(Evec, dtype=struct.dtypec)









if __name__ == "__main__":
    ## ---------- Module Doc
    #print forEplanewave.__doc__
#    print forEfocused.__doc__
    
    
    ## TEST INCIDENT FIELD ROUTINE
    from mayavi import mlab
    import structures as structs
    
    posX=0;posY=0;posZ=1000
    MAXDIST=200
    xm,ym,zm = structs.rectwire(10,20,20,20).T
    zm += 50   ## z-offset
    dist = np.sqrt((xm-posX)**2 + (ym-posY)**2 + (zm-posZ)**2)
    xm = xm[dist>MAXDIST]
    ym = ym[dist>MAXDIST]
    zm = zm[dist>MAXDIST]
    
    simDict = {'elambda':[800], 'atheta':[0], 
               'xm':xm, 'ym':ym, 'zm':zm,
               'n1':1,'n2':1,'n3':1}
    
    
#    FIELD = focused(simDict, 1,1, 100,100, NA=1.)
#    FIELD = np.reshape(FIELD, (len(FIELD)/3, 3))
#    X,Y,Z = FIELD.T
#    
#    mlab.figure()
#    mlab.quiver3d(xm,ym,zm, X.real, Y.real, Z.real)
#    mlab.orientation_axes()
#    mlab.axes()
#    mlab.title("Focused Planewave")
    
    
    
    fieldtype = 'e'
    FIELD = planewave(simDict,  800,0,   returnField=fieldtype)
#    FIELD = magDipole(simDict,  800,0,   posX,posY,posZ,   1,0,0,  returnField=fieldtype)
#    FIELD = elecDipole(simDict,  800,0,   posX,posY,posZ,   1,0,0,  returnField=fieldtype)
    FIELD = np.reshape(FIELD, (len(FIELD)/3, 3))
    X,Y,Z = FIELD.T
    
    
    
    
#    from pyGDM.visu.common import animateNearfield3D
#    NF = np.array([xm,ym,zm, X.real,X.imag, Y.real,Y.imag, Z.real,Z.imag]).T
#    animateNearfield3D(NF)
    
    
    
#    fig = mlab.figure(size=(1000,1000))
    mlab.quiver3d(xm,ym,zm, X.real, Y.real, Z.real)
    mlab.orientation_axes()
    mlab.axes()
    if fieldtype=='E':
        mlab.title("mag. dipole - Efield")
##        mlab.savefig("mag_dp_Efield.png")
    if fieldtype=='B':
        mlab.title("mag. dipole - Bfield")
##        mlab.savefig("mag_dp_Bfield.png")
#    
    mlab.show()








