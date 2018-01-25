#!/usr/bin/env python3
# system modules
import warnings

# external modules
import numpy as np

def deg2rad(x):
    """
    Convert angle in degrees to radians
    """
    return x / 180 * np.pi

def rad2deg(x):
    """
    Convert angle in radians to degrees
    """
    return x * 180 / np.pi

def wind_vector_angle(
    u,v,origin=True,clockwise=True):
    """
    Calculate the wind direction from its vector components in radians. This
    direction is the angle from the positive axis of ordinates ("y-axis")
    either to the arrow tip (if ``origin=False``) or to the inverted
    arrow tip (if ``origin=True``) in ``clockwise`` direction.
    Defaults to the meteorological wind direction definition (``origin=True``
    and ``clockwise=True``).

    Args:
        u (float): latitudinal wind vector component
        v (float): longitudinal wind vector component
        origin (bool, optional): Return the origin wind
            direction (i.e. FROM where the wind originates). Defaults to
            ``True``. Otherwise, return the direction of the wind arrow tip.
        clockwise (bool, optional): Return the wind direction in clockwise or
            anti-clockwise direction. Defaults to ``True``.

    Returns:
        float : wind direction angle in radians
    """
    u,v = np.broadcast_arrays(u,v)
    angle = np.mod((
        # atan2 = anti-clockwise angle from positive y-axis
        + (-1 if clockwise else 1) * (np.arctan2(v,u) - np.pi/2) \
        # use reverted angle if wanted
        + (np.pi if origin else 0) \
        # add a full circle to make sure angle is positive
        + 2*np.pi ) \
        , 2*np.pi)
    zerowind = np.logical_and(u==0,v==0)
    n_zerowind = zerowind.sum()
    if n_zerowind:
        warnings.warn("{} zero-wind values were masked".format(n_zerowind))
    angle = np.where(zerowind,np.nan,angle)
    return angle
