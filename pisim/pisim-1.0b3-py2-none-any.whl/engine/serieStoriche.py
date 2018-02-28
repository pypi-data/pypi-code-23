# -*- coding: utf-8 -*-

"""Module computing sequences of indexes used in computations elsewhere.

Module's content
================

"""

from common import getIntSempliceMedio
from random import uniform
import math


def getSerieTassi(anni, media, delta, avgArray, lowerLimit=-0.5,
                  upperLimit=1.0):
    """Compute a sequence of indexes (internally used).

    This procedure implements the indexes random generation.
    A customly modified version of the uniform pseudo-random generator
    is implemented. It has the following characteristics:

    * A smoothing operator is applied to any generated sample,
      so that year-over-year oscillations get reduced.
    * Such a smoothing is implemented by averaging the sample with
      the current average index - that is to say the yearly average
      simple index computed from the indexes generated since then.
    * The smoothing operation effectiveness is tunable by changing two
      parameters, which basically are the exponents of the sample and the
      current average index. The greater an exponent, the strongest
      is the contribution of that index to the smoothed result.
    * Samples - before smoothing - are computed taking into account
      the samples generated since then, so that the actual average is kept
      as close as possible to the intended one. Basically each sample
      is randomly picked in the interval having the current average index
      as center and the passed delta as max variation (upper and lower
      limits hold.)

    :param int anni: Sequence length.
    :param float media: Sequence average value.
    :param float delta: Samples max variation.
    :param list(float) avgArray: Smoothing array. First item is the
        exponent of the current average, while the second if the exponent
        of the sample.
    :param float lowerLimit: Samples smallest value.
    :param float upperLimit: Samples greatest value.
    :returns: The sequence of indexes.
    :rtype: list(float)

    """
    def getTasso(media, delta, lowerLimit, upperLimit):
        tasso = uniform(media-delta, media+delta)
        if tasso < lowerLimit:
            tasso = lowerLimit
        elif tasso > upperLimit:
            tasso = upperLimit
        return tasso

    def wtdSample(sample, corrente, fAvgArray):
        return math.pow(1+corrente, fAvgArray[0]) * \
            math.pow(1+sample, fAvgArray[1]) - 1

    fAvgArray = [float(x)/sum(avgArray) for x in avgArray]
    corrente = getTasso(media, delta, lowerLimit, upperLimit)
    serie = [corrente]
    for j in range(1, anni):
        nuovaMedia = \
            math.pow(1+media, j+1)/reduce(lambda x, y: x*(1+y), serie, 1)-1
        sample = getTasso(nuovaMedia, delta, lowerLimit, upperLimit)
        serie.append(wtdSample(sample, corrente, fAvgArray))
        corrente = getIntSempliceMedio(serie)

    return serie


def getInflazione(anni, tassoMedio, variazione=0):
    """Generate a sequence of inflation indexes.

    :param int anni: sequence length.
    :param float tassoMedio: average inflation index.
    :param float variazione: if !=0, indexes are randomly (and uniformly)
        generated, this parameter being the greatest variation
        from the average.
        Otherwise the sequence will be composed by a repetition of the
        average value.
    :returns: The sequence of indexes.
    :rtype: list(float)
    """
    retVal = getSerieTassi(anni, tassoMedio, variazione, [1, 1], 0)
    return [round(x, 5) for x in retVal]


def getRivalutazioneSalario(serieInflazione, rivalutazioneAnno=0, frequenza=1):
    """Generate a sequence of salary revalutation indexes.

    :param list(float) serieInflazione:
        sequence of inflation indexes as returned by :py:func:`getInflazione`.
    :param float rivalutazioneAnno: average yearly salary revalutation,
        inflation apart.
    :param float frequenza: interval (i.e. number of years) with which
        the revalutation is applied.
    :returns: The sequence of yearly salary revalutation indexes.
    :rtype: list(float)
    """
    rivalutazione = math.pow(1+rivalutazioneAnno, frequenza)-1
    anni = len(serieInflazione)

    retVal = [(1+serieInflazione[i]) *
              (1+(rivalutazione if (i+1) % frequenza == 0 else 0))-1
              for i in range(anni)]

    return [0.0]+[round(x, 5) for x in retVal][:-1]


def getRivalutazioneAccantonamento(anni, inflazioneMedia, rivMedia,
                                   deltaVariazione):
    """Generate a sequence of fondo pensione revalutation indexes.

    :param int anni: Sequence length.
    :param float inflazioneMedia: Average inflation index.
    :param float rivMedia: Average yearly revalutation index,
        inflation apart.
    :param float deltaVariazione: If !=0, indexes are randomly
        (and uniformly) generated, this parameter being the greatest variation
        from the average. Otherwise sequence will be a repetition
        of the same value.
    :returns: The sequence of yearly revalutation indexes.
    :rtype: list(float)
    """
    retVal = [(1+x)*(1+inflazioneMedia)-1
              for x in getSerieTassi(anni, rivMedia, deltaVariazione, [1, 1])]
    return [round(x, 5) for x in retVal]
