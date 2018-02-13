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
"""
Collection of dielectric functions and tools to load tabulated data
"""
import numpy as np

#==============================================================================
# Internal definitions
#==============================================================================
class _interp1dPicklable:
    """wrapper for pickleable version of `scipy.interpolate.interp1d`
    
    **Note:** there might be still pickle-problems with certain c / fortran 
    wrapped libraries
    
    From: http://stackoverflow.com/questions/32883491/pickling-scipy-interp1d-spline
    """
    def __init__(self, xi, yi, **kwargs):
        from scipy.interpolate import interp1d
        self.xi = xi
        self.yi = yi
        self.args = kwargs
        self.f = interp1d(xi, yi, **kwargs)

    def __call__(self, xnew):
        return self.f(xnew)

    def __getstate__(self):
        return self.xi, self.yi, self.args

    def __setstate__(self, state):
        from scipy.interpolate import interp1d
        self.f = interp1d(state[0], state[1], **state[2])




#==============================================================================
# General purpose
#==============================================================================
class dummy(object):
    """constant index
    
    Material with spectrally constant refractive index
    
    Parameters
    ----------
    n : complex, default: (2.0 + 0.0j)
        complex refractive index of constant material (returned dielectric 
        function will be n**2)
        
    """
    
    def __init__(self, n=(2.0 + 0.0j)):
        """Define constant material"""
        self.n = complex(n)
        self.__name__ = 'constant index material, n={}'.format(self.n)
    
    def epsilon(self, wavelength):
        """Dummy material: Constant dielectric function
    
        constant dielectric function material
        
        Parameters
        ----------
        wavelength : real
            wavelength at which to evaluate dielectric function (in nm)
        
        """
        eps = complex(self.n**2)
        return eps


class fromFile(object):
    """tabulated dispersion
    
    Use tabulated data provided from textfile for the complex material 
    refractive index
    
    Parameters
    ----------
    refindex_file : str
        path to text-file with the tabulated refractive index 
        (3 whitespace separated columns: #1 wavelength, #2 real(n), #3 imag(n))
        
        Data can be obtained e.g. from https://refractiveindex.info/ 
        using the *"Full database record"* export function.
    
    unit_wl : str, default: 'micron'
        Units of the wavelength in file, one of ['micron', 'nm']
    
    interpolate_order : int, default: 1
        interpolation order for data (1: linear, 2: square, 3: cubic)
        "1" uses `numpy.interp`, "2" and "3" require `scipy` 
        (using `scipy.interpolate.interp1d`)
    
    """
    
    def __init__(self, refindex_file, unit_wl='micron', interpolate_order=1):
        """Use tabulated dispersion"""
        wl, n, k = np.loadtxt(refindex_file).T
        
        if unit_wl.lower() in ['micron', 'microns', 'um']:
            factor_wl = 1.0E3  # micron --> nm
        elif unit_wl.lower() in ['nanometer', 'nm']:
            factor_wl = 1
        else:
            raise ValueError("`unit_wl` must be one of ['micron', 'nm'].")
        self.wl = wl * factor_wl
        self.n_real = n
        self.n_imag = k
        self.n_cplx = self.n_real + 1.0j*self.n_imag
        
        self.interpolate_order = interpolate_order
        if self.interpolate_order > 1:
            self.f = _interp1dPicklable(self.wl, self.n_cplx, kind=self.interpolate_order)
        
        self.__name__ = 'tabulated n ({})'.format(refindex_file)
    
    def epsilon(self, wavelength):
        """Tabulated interpolated dielectric function
    
        constant dielectric function material
        
        Parameters
        ----------
        wavelength : real
            wavelength at which to evaluate dielectric function (in nm)
        
        """
        if self.interpolate_order == 1:
            n_r = np.interp(wavelength, self.wl, self.n_real)
            n_i = np.interp(wavelength, self.wl, self.n_imag)
            eps = (n_r + 1j*n_i)**2
        else:
            eps = self.f(wavelength)**2
        return eps




#==============================================================================
# Metals
#==============================================================================
class gold(object):
    """gold index
    
    Complex dielectric function of gold from:
    P. B. Johnson and R. W. Christy. Optical Constants of the Noble Metals, 
    Phys. Rev. B 6, 4370-4379 (1972)
    
    Parameters
    ----------
    interpolate_order : int, default: 1
        interpolation order for data (1: linear, 2: square, 3: cubic)
        "1" uses `numpy`, "2" and "3" require `scipy` (`scipy.interpolate.interp1d`)
    
    """
    __name__ = 'Gold, Johnson/Christy'
    
    def __init__(self, interpolate_order=1):
        """gold dispersion"""
        self.wl = 1239.19/np.array([0.1,0.2,0.3,0.4,0.5,0.5450000,0.5910000,0.6360000,0.64,0.77,0.89,1.02,1.14,1.26,1.39,1.51,1.64,1.76,1.88,2.01,2.13,2.26,2.38,2.50,2.63,2.75,2.88,3.00,3.12,3.25,3.37,3.50,3.62,3.74,3.87,3.99,4.12,4.24,4.36,4.49,4.61,4.74,4.86,4.98,5.11,5.23,5.36,5.48,5.60])[::-1]
        self.n_real = np.array([25.17233,7.60352,3.53258,2.02586,1.299091,1.097350,0.9394755,0.8141369,0.92,0.56,0.43,0.35,0.27,0.22,0.17,0.16,0.14,0.13,0.14,0.21,0.29,0.43,0.62,1.04,1.31,1.38,1.45,1.46,1.47,1.46,1.48,1.50,1.48,1.48,1.54,1.53,1.53,1.49,1.47,1.43,1.38,1.35,1.33,1.33,1.32,1.32,1.30,1.31,1.30])[::-1]
        self.n_imag = np.array([77.92804,43.34848,29.52751,22.25181,17.77038,16.24777,14.94747,13.82771,13.78,11.21,9.519,8.145,7.15,6.35,5.66,5.08,4.542,4.103,3.697,3.272,2.863,2.455,2.081,1.833,1.849,1.914,1.948,1.958,1.952,1.933,1.895,1.866,1.871,1.883,1.898,1.893,1.889,1.878,1.869,1.847,1.803,1.749,1.688,1.631,1.577,1.536,1.497,1.460,1.427])[::-1]
        self.n_cplx = self.n_real + 1.0j*self.n_imag
        
        self.interpolate_order = interpolate_order
        if self.interpolate_order > 1:
            self.f = _interp1dPicklable(self.wl, self.n_cplx, kind=self.interpolate_order)
    
    def epsilon(self, wavelength):
        """Gold dielectric function
        
        Parameters
        ----------
        wavelength: real
            wavelength at which to evaluate dielectric function (in nm)
        
        """
        if self.interpolate_order == 1:
            n_r = np.interp(wavelength, self.wl, self.n_real)
            n_i = np.interp(wavelength, self.wl, self.n_imag)
            eps = (n_r + 1j*n_i)**2
        else:
            eps = self.f(wavelength)**2
        return eps


class alu(object):
    """alu index
    
    Complex dielectric function of aluminium from:
    A. D. Rakić, A. B. Djurišic, J. M. Elazar, and M. L. Majewski. 
    Optical properties of metallic films for vertical-cavity optoelectronic 
    devices, Appl. Opt. 37, 5271-5283 (1998)
    
    Parameters
    ----------
    interpolate_order : int, default: 1
        interpolation order for data (1: linear, 2: square, 3: cubic)
        "1" uses `numpy`, "2" and "3" require `scipy` (`scipy.interpolate.interp1d`)

    """
    __name__ = 'Aluminium, Rakic'
    
    def __init__(self, interpolate_order=1):
        """alu dispersion"""
        self.wl = 1239.19/np.array([0.1,0.2,0.3,0.4,0.5,0.5450000,0.5910000,0.6360000,0.64,0.77,0.89,1.02,1.14,1.26,1.39,1.51,1.64,1.76,1.88,2.01,2.13,2.26,2.38,2.50,2.63,2.75,2.88,3.00,3.12,3.25,3.37,3.50,3.62,3.74,3.87,3.99,4.12,4.24,4.36,4.49,4.61,4.74,4.86,4.98,5.11,5.23,5.36,5.48,5.60])[::-1]
        self.n_real = np.array([28.842,12.493,7.0377,4.42,3.0379,2.6323,2.3078,2.0574,2.0379,1.5797,1.3725,1.3007,1.3571,1.5656,2.1077,2.7078,2.3029,1.6986,1.3879,1.2022,1.0767,.95933,.86160,0.77308,0.68783,0.61891,0.55416,0.50256,0.45783,0.41611,0.38276,0.35151,0.32635,0.30409,0.28294,0.26559,0.24887,0.23503,0.22254,0.21025,0.19997,0.18978,0.18114,0.17313,0.16511,0.15823,0.15126,0.14523,0.13956])[::-1]
        self.n_imag = np.array([99.255,55.533,39.303,30.285,24.498,22.52,20.782,19.304,19.182,15.847,13.576,11.666,10.250,9.0764,8.1465,8.1168,8.4545,8.0880,7.5779,7.1027,6.7330,6.3818,6.0889,5.8179,5.5454,5.3107,5.0734,4.8691,4.6779,4.4849,4.3185,4.1501,4.0048,3.8682,3.7294,3.6090,3.4862,3.3793,3.2782,3.1745,3.0838,2.9906,2.9088,2.8308,2.7502,2.6792,2.6056,2.5406,2.4783])[::-1]
        self.n_cplx = self.n_real + 1.0j*self.n_imag
        
        self.interpolate_order = interpolate_order
        if self.interpolate_order > 1:
            self.f = _interp1dPicklable(self.wl, self.n_cplx, kind=self.interpolate_order)
    
    def epsilon(self, wavelength):
        """Aluminium dielectric function
        
        Parameters
        ----------
        wavelength: real
            wavelength at which to evaluate dielectric function (in nm)
        
        """
        if self.interpolate_order == 1:
            n_r = np.interp(wavelength, self.wl, self.n_real)
            n_i = np.interp(wavelength, self.wl, self.n_imag)
            eps = (n_r + 1j*n_i)**2
        else:
            eps = self.f(wavelength)**2
        return eps




#==============================================================================
# Dielectrica
#==============================================================================
class silicon(object):
    """silicon index
    
    Complex dielectric function of silicon from:
    Edwards, D. F. in Handbook of Optical Constants of Solids 
    (ed. Palik, E. D.) 547–569 (Academic Press, 1997).

    Parameters
    ----------
    interpolate_order : int, default: 1
        interpolation order for data (1: linear, 2: square, 3: cubic)
        "1" uses `numpy`, "2" and "3" require `scipy` (`scipy.interpolate.interp1d`)
    
    """
    __name__ = 'Silicon, Palik'
    
    def __init__(self, interpolate_order=1):
        """silicon dispersion"""
        self.wl = 1239.19/np.array([0.70,0.80,0.90,1.00,1.10,1.20,1.3,1.4,2.0,2.2,2.4,2.6,2.8,3.0,3.2,3.4,3.6,3.8,4.0,4.4,4.8])[::-1]
        self.n_real = np.array([3.459338,3.476141,3.496258,3.519982,3.539048,3.57,3.6,3.63,3.94,4.08,4.26,4.5,4.82,5.31,6.18,6.53,5.25,5.01,4.91,2.92,1.6])[::-1]
        self.n_imag = np.array([0.0000000,0.0000000,0.0000000,0.0000000,0.000017,0.00038,0.00157,0.00346,0.01,0.01,0.01,0.02,0.11,0.25,0.65,2.93,3.13,3.33,3.74,5.28,3.91])[::-1]
        self.n_cplx = self.n_real + 1.0j*self.n_imag
        
        self.interpolate_order = interpolate_order
        if self.interpolate_order > 1:
            self.f = _interp1dPicklable(self.wl, self.n_cplx, kind=self.interpolate_order)
    
        
    def epsilon(self, wavelength):
        """Silicon dielectric function
        
        Parameters
        ----------
        wavelength: real
            wavelength at which to evaluate dielectric function (in nm)
        
        """
        if self.interpolate_order == 1:
            n_r = np.interp(wavelength, self.wl, self.n_real)
            n_i = np.interp(wavelength, self.wl, self.n_imag)
            eps = (n_r + 1j*n_i)**2
        else:
            eps = self.f(wavelength)**2
        return eps


