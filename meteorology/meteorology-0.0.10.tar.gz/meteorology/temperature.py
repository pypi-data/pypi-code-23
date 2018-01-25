#!/usr/bin/env python3

# system modules
import warnings

# internal modules
from .constants import zero_celsius_in_kelvin

# external modules
import numpy as np

def cel2kel(T):
    """ 
    Convert temperatures in degrees Celsius to degrees Kelvin

    Args:
        T (numpy.ndarray): temperature in degrees Celsius

    Returns:
        numpy.ndarray : given temperature converted to degrees Kelvin
    """
    # convert to an array
    celsius = np.asanyarray(T).astype(float)
    oldshape = celsius.shape
    celsius = celsius.reshape(-1)
    # convert to kelvin
    kelvin = celsius + zero_celsius_in_kelvin
    # replace invalid temperatures
    invalid = kelvin < 0
    if invalid.any():
        warnings.warn("{} temperatures below 0 Kelvin masked with NaN".format(
            invalid.sum()))
        kelvin[invalid] = np.nan
    return kelvin.reshape(oldshape)

def kel2cel(T):
    """ 
    Convert temperatures in degrees Kelvin to degrees Celsius

    Args:
        T (numpy.ndarray): temperature in degrees Kelvin

    Returns:
        numpy.ndarray : given temperature converted to degrees Celsius
    """
    # convert to an array
    kelvin = np.asanyarray(T).astype(float)
    oldshape = kelvin.shape
    kelvin = kelvin.reshape(-1)
    invalid = kelvin < 0
    if invalid.any():
        warnings.warn("{} temperatures below 0 Kelvin masked with NaN".format(
            invalid.sum()))
        kelvin[invalid] = np.nan
    # convert to kelvin
    celsius = kelvin - zero_celsius_in_kelvin
    # replace invalid temperatures
    return celsius.reshape(oldshape)
