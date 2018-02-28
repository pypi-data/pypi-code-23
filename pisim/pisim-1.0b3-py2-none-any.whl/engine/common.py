# -*- coding: utf-8 -*-

"""Functions performing basic, common computations.

Module's content
================

"""

import math
import numpy


def mean(samples):
    """Compute the average of a set of samples.

    :param list(float) samples: samples whose average has to be computed.
    :returns: the average.
    :rtype: float
    """
    return sum(samples)/len(samples)


def stdDev(samples):
    """Compute the standard deviation of a set of samples.

    :param list(float) samples: samples whose std. dev. has to be computed.
    :returns: the standard deviation.
    :rtype: float
    """
    return math.pow(
        sum([(x-mean(samples))*(x-mean(samples))
             for x in samples]), 0.5)/len(samples)


def VAN(serieFlussi, serieTassi):
    """Compute the Valore Attuale Netto of a sequence of money fluxes.

    Details on VAN definition (in Italian) can be found at
    `[VAN on Wikipedia] <https://it.wikipedia.org/wiki/Valore_attuale_netto>`_.

    :param list(float) serieFlussi:
        money movements, both positive (money earnt) and negative
        (money given), for each time period.
    :param list(float) serieTassi: yield index for each time period.
    :returns: The VAN.
    :rtype: float
    """
    van = [serieFlussi[i]/reduce(lambda x, y: x*(1+y), serieTassi[:i], 1)
           for i in range(len(serieFlussi))]
    van = round(sum(van), 2)
    return van


def VAN1(valore, serieTassi):
    """Compute the VAN of a single money movement at a given point in time.

    This function is just a wrapper of a given call configuration of
    :py:func:`VAN`.

    This function computes the VAN of a single money flux which happens
    at a precise point in time, knowing the sequence of indexes for
    all the time periods (the one when the money movement happens as well as
    all precededing.)

    As an example, if the yields are the year-over-year inflaction indices
    and the input value is the amont of money owed/due in the future,
    this functions computes the amount's actual value.

    :param float valore: the value on which the VAN has to be computed.
    :param list(float) serieTassi: the sequence of yield indices for all the
        time periods from today till the moment when the money is owed/due.
    :returns: The value's VAN.
    :rtype: float
    """
    return VAN([0]*len(serieTassi)+[valore], serieTassi)


def TIR(serieFlussi):
    """Compute the TIR of a sequence of money fulxes.

    Details on TIR definition (in Italian) can be found at
    `[TIR on Wikipedia]
    <https://it.wikipedia.org/wiki/Tasso_interno_di_rendimento>`_.

    :param list(float) serieFlussi: sequence of money movements whose
        TIR has to be computed.
    :returns: the TIR.
    :rtype: float
    """
    roots = [1/r-1 for r in numpy.roots(serieFlussi[::-1]) if abs(r)]
    return [r.real for r in roots
            if abs(r.real) < 1 and abs(r.imag/r.real) <= 1e-5][0]


def getSerieTassiComposti(serieTassiSemplici):
    """Compute the sequence of compound indexes from simple ones.

    :param list(float) serieTassiSemplici:
        The sequence of simple indexes, one for each time period.
    :returns: The sequence of compound indexes, one for each time period.
    :rtype: list(float)
    """
    def tComp(serie, n):
        return reduce(lambda x, y: x*(1+y), serie[:i+1], 1)

    return [tComp(serieTassiSemplici, i)-1
            for i in range(len(serieTassiSemplici))]


def getIntSempliceMedio(serieTassi):
    """Compute the average simple index of a sequence of simple indexes.

    :param list(float) serieTassi: the sequence of time periods simple indexes.
    :returns: The average simple index.
    :rtype: float
    """
    intComposto = reduce(lambda x, y: x*(1+y), serieTassi, 1) - 1
    return math.pow(1+intComposto, 1.0/len(serieTassi)) - 1


def getIrpef(valore):
    """Compute the due IRPEF tax of a money amount.

    :param float valore: The money amount whose IRPEF has to be computed.
    :returns: the due IRPEF
    :rtype: float
    """
    scaglioni = [0, 15000, 28000, 55000, 75000]
    aliquote = [None, 0.23, 0.27, 0.38, 0.41, 0.43]

    retVal = 0.0
    for i in range(1, len(scaglioni)):
        if valore <= scaglioni[i]:
            retVal += (valore-scaglioni[i-1]) * aliquote[i]
            return round(retVal, 2)
        retVal += (scaglioni[i]-scaglioni[i-1]) * aliquote[i]
    retVal += (valore-scaglioni[-1]) * aliquote[-1]

    return round(retVal, 2)
