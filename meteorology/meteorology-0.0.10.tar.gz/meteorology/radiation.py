#!/usr/bin/env python3

# system modules
import warnings

# internal modules
from .temperature import cel2kel,kel2cel
from .constants import stefan_boltzmann_constant

# external modules
import numpy as np

def blackbody_radiation(T):
    r""" 
    Calculate the total emitted radiation for a blackbody surface at a given
    temperature according to the Stefan-Boltzmann law:

    .. math::

        I_\mathrm{total} = \sigma \, T ^ 4

    Args:
        T (numpy.ndarray): temperature in Kelvin

    Returns:
        numpy.ndarray : the total emitted blackbody radiation
        :math:`\left[I_\mathrm{total}\right] = \frac{W}{m^2}`
    """
    # convert to an array
    kelvin = cel2kel(kel2cel(T))
    oldshape = kelvin.shape
    kelvin = kelvin.reshape(-1)

    rad = stefan_boltzmann_constant * kelvin ** 4

    return rad.reshape(oldshape)

def adjust_radiation_temperature_to_other_emissivity(
    T,emissivity_old = 1,emissivity_new = 1,T_ambient=0):
    r""" 
    Given a radiation temperature :math:`T` (``T``) that was obtained using an
    emissivity of :math:`\epsilon_\mathrm{old}` (``emissivity_old``), calculate
    an adjusted radiation temperature :math:`T_\mathrm{new}` that would have
    been obtained if the emissivity had been :math:`\epsilon_\mathrm{new}`
    (``emissivity_new``), optionally taking the reflected ambient radiation
    temperature :math:`T_\mathrm{ambient}` (``T_ambient``) into account:

    .. math::
        
        T_\mathrm{new} = \sqrt[4]{
            \frac{
                \epsilon_\mathrm{old} \, T ^ 4 - 
                \left(1-\epsilon_\mathrm{new}\right) \, T_\mathrm{ambient} ^ 4
                }{
                \epsilon_\mathrm{new}
                }
            }

    Args:
        T (numpy.ndarray): the obtained radiation temperature
        emissivity_new (numpy.ndarray, optional): the desired new
            emissivity. Defaults to ``1``.
        emissivity_old (numpy.ndarray, optional): the emissivity used
            to obtain ``T``. Defaults to ``1``.
        T_ambient (numpy.ndarray, optional): the ambient radiation temperature.
            Defaults to ``0``, meaning no influence.
    """
    eps_old = np.asanyarray(emissivity_old).astype(float)
    invalid = np.logical_or(eps_old<0,eps_old>1)
    if invalid.any():
        warnings.warn("Masking {} invalid emissivity_old values outside the " 
            "physical range [0;1] with NaN".format(invalid.sum()))
        eps_old = np.where(invalid, np.nan, eps_old)
    eps_new = np.asanyarray(emissivity_new).astype(float)
    invalid = np.logical_or(eps_new<=0,eps_new>1)
    if invalid.any():
        warnings.warn("Masking {} invalid emissivity_new values outside the " 
            "physical range (0;1] with NaN".format(invalid.sum()))
        eps_new = np.where(invalid, np.nan, eps_new)

    T_old = cel2kel(kel2cel(T))

    T_new = ( 
        ( (eps_old * T_old **4) - (1 - eps_new) * T_ambient ** 4) / eps_new 
        ) ** (1/4)

    return T_new
