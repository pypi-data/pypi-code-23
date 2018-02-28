# -*- coding: utf-8 -*-

"""Scenario simulations for fondo pensione and TFR.

Module's content
================

"""

from ..engine.serieStoriche import getInflazione, getRivalutazioneSalario, \
                                   getRivalutazioneAccantonamento
from ..engine.common import mean, stdDev
from ..engine.fondoPensione import getPiano as getPianoFp
from ..engine.tfr import getPiano as getPianoTfr
from ..engine import report
from ..dataLoadStore.common import DescIo
import errors

import math


class FpSim:
    """Scenario simulation class.

    This class is just a container of the simulation execution method.
    It's not meant to be instanced.
    """

    class Scenarios:
        """Scenarios type ID.

        As of the current implementation, three scenarios types
        have been identified:

        * Worst: ID = 0
        * Best: ID = 1
        * Normal: ID = 2

        They have the following characteristics:

        * Worst: Increasing inflation, decreasing fondo pensione revalutation.
        * Best: Opposite of worst.
        * Normal: Random arrangement of both inflation and revalutation.
        """

        WORST = 0   # -- increasing inflazione, decreasing rivalutazione FP
        BEST = 1    # -- decreasing inflazione, increasing rivalutazione FP
        NORMAL = 2  # -- all random series taken as they're generated

    @staticmethod
    def _getStats(samples):
        """Compute mean and 95% confidence interval of a samples sequence.

        :param list(float) samples: samples on which mean and standard
            interval have to be computed.
            List is supposed having 30 items.
        :returns: Average and standard interval.
        :rtype: (float, float)
        :raises NotPositiveYearsError: if combined descriptors values
            lead to a non-positive number of plan development years.
        :raises TooManyYearsError: if the plan develops for more than
            35 years.
        """
        nSamples = len(samples)
        mn = mean(samples)
        confInt = \
            stdDev(samples) * \
            math.pow(nSamples, 0.5) / \
            math.pow(nSamples-1, 0.5)
        confInt *= 1.699  # -- 95% confidence interval, 30 samples
        return mn, confInt

    @staticmethod
    def run(descs, scenario):
        """Simulate scenario described by descriptors and return values.

        :param dict descs: Scenario describing descriptors.
            They are the same as returned by I/O procedures in
            :py:mod:`.dataLoadStore`, report apart.
        :param int scenario: Scenario type identifies, taken from
            :py:class:`Scenarios`.
        :returns: Same dictionary as returned by
            :py:func:`.engine.report.get`, with values replaced with a
            2-keys dictionary: ``{'average': float, 'confInt': float}``.
        :rtype: dict
        """
        anni = descs['dipendente']['nascita'].year + \
            descs['pensione']['etaPensionamento'] - \
            descs['dipendente']['inizioPiano'].year + 1

        if anni <= 0:
            raise errors.NotPositiveYearsError(anni)
        elif anni > 35:
            raise errors.TooManyYearsError(anni, 35)

        nSamples = 30
        tmpResults = {}
        for _ in range(nSamples):
            inflazione = getInflazione(
                anni,
                descs['inflazione']['tassoMedio'],
                descs['inflazione']['variazione'])
            rivSalario = getRivalutazioneSalario(
                inflazione,
                descs['salario']['rivalutazione']['valore'],
                descs['salario']['rivalutazione']['frequenza'])
            rivFP = getRivalutazioneAccantonamento(
                anni,
                descs['inflazione']['tassoMedio'],
                descs['fp']['accumulo']['rivalutazione']['valore'],
                descs['fp']['accumulo']['rivalutazione']['variazione'])

            if scenario != FpSim.Scenarios.NORMAL:
                inflazione = \
                    sorted(inflazione,
                           reverse=(scenario == FpSim.Scenarios.BEST))
                rivFP = \
                    sorted(rivFP, reverse=(scenario == FpSim.Scenarios.WORST))

            pianoFP = getPianoFp(
                descs,
                inflazione,
                rivSalario,
                rivFP)
            pianoTfr = getPianoTfr(descs, inflazione, rivSalario)

            samples = report.get(descs, pianoFP, pianoTfr)
            del samples['descs']
            del samples['tassi']
            samples = DescIo.serializeDesc(samples)

            tmpResults = \
                {k: (tmpResults[k] if (k in tmpResults) else [])+[samples[k]]
                    for k in samples}

        tmpResults = \
            {k: list(FpSim._getStats(tmpResults[k])) for k in tmpResults}
        tmpResults = \
            {k: {'average': tmpResults[k][0], 'confInt': tmpResults[k][1]}
                for k in tmpResults}

        return DescIo.deserializeDesc(DescIo.serializeDesc(tmpResults))
