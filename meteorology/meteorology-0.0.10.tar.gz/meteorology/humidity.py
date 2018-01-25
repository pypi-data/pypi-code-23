#!/usr/bin/env python3

# system modules
import warnings

# internal modules
from .temperature import kel2cel

# external modules
import numpy as np

def saturation_water_vapour_pressure(T, over = "auto", param = "magnus"):
    r""" 
    Saturation water vapour pressure over ``over`` according to the
    parametisation ``param``.
    

    Args:
        T (numpy.ndarray): temperature in degrees Kelvin
        over (str, optional): use the parameterisation over ``"water"`` or
            ``"ice"`` or ``"auto"`` (the default) to use ``"water"`` for
            temperatures over and including :math:`0^\circ C` and ``"ice"``
            below.
        param (str, optional): the parameterisation to use. Defaults to
            ``"magnus"``. Available parameterisations are: 
            
            ``"magnus"`` 
                `Magnus-Formula`_


    Returns:
        numpy.ndarray : the saturation water vapour pressure 
        :math:`\left[e_\mathrm{s}\right] = Pa`

    .. _Magnus-Formula: https://de.wikipedia.org/w/index.php?oldid=162431872
    """
    celsius = kel2cel(T) # convert to Celsius

    if param == "magnus":
        # the Magnus parameterisations
        params = { 
            "water": {
                "A": 6.112e2, # Pa
                "B": 17.62, # C^-1
                "C": 243.12, # C
                "low": -45, # lower bound C
                "high": 65, # upper bound C
                },
            "ice": {
                "A": 6.112e2, # Pa
                "B": 22.46, # C^-1
                "C": 272.62, # C
                "low": -65, # lower bound C
                "high": 0.01, # upper bound C
                },
            }
        if over == "auto":
            over0celsius = celsius >= 0
            autoparam = {
                c:np.where(over0celsius,params["water"][c],params["ice"][c]) \
                    for c in params["water"].keys()}
            autoparam.update({
                "low":params["ice"]["low"],
                "high":params["water"]["high"],
                })
            params.update({"auto":autoparam})

        # get the appropriate parameterisation
        const = params.get(over)

        # check bounds
        outside = np.logical_or(celsius<const["low"],celsius>const["high"])
        if outside.any():
            warnings.warn("There are {} temperatures outside the " 
                "parameterisation scope [{:.2f};{:.2f}] °C".format(
                outside.sum(),const["low"],const["high"]))

        if not const: # pragma: no cover
            raise ValueError("unknown 'over' string '{}'".format(over))
            
        e_s = const["A"] * np.exp((const["B"]*celsius) / (const["C"] + celsius))
    else: # pragma: no cover
        raise ValueError("unknown parameterisation '{}'".format(param))

    return e_s
