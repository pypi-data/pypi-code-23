# -*- coding: utf-8 -*-

"""Module implementing the computation of the development of fondo pensione.

Module's content
================

"""

from common import getIrpef, TIR
import math
import errors


def getPiano(desc, serieInflazione, serieRivSalario, serieRivAccumulo):
    """Compute tehe year-over-year develop of fondo pensione.

    :param dict desc:
        dictionary containing all configuration descriptors.
    :param list(float) serieInflazione:
        list of inflation indexes.
    :param list(float) serieRivSalario:
        list of yearly salary revalutation indexes, inflation apart.
    :param list(float) serieRivAccumulo:
        list of yearly revalutation indexes of fondo pensione ammassed money,
        inflation apart.
    :returns: the dictionary containing the fondo pensione elaboration results.
    :rtype: dict
    :raises EtaPensionamentoNotFoundError:
        if the transformation factor from last salary to retirement wage
        for the given sex and retirement age is not found in
        desc's fp.rendita descriptor.

    *desc* parameter shall have the following format::

        {
            'dipendente': "descriptor for dipendente",
            'salario': "descriptor for salario",
            'pensione': "descriptor for pensione",
            'inflazione':  "descriptor for inflazione",
            'fp': {
                'base': "descriptor for fondo pensione, base",
                'accumulo': "descriptor for fondo pensione, accumulo",
                'rendita': "descriptor for fondo pensione, rendita"
            }
        }

    For further info about descriptors mentioned above, see the following:

    * Dipendente: :py:class:`.DipendenteDescIo`
    * Salario: :py:class:`.SalarioDescIo`
    * Pensione: :py:class:`.PensioneDescIo`
    * Inflazione: :py:class:`.InflazioneDescIo`
    * Fondo pensione, base: :py:class:`.FpBaseDescIo`
    * Fondo pensione, accumulo: :py:class:`.FpAccumuloDescIo`
    * Fondo pensione, rendita: :py:class:`.FpRenditaDescIo`

    The returned descriptor is defined as follows::

        {
            'tassi':
            {
                'inflazione': "passed serieInflazione",
                'rivSalario': "passed serieRivSalario",
                'rivAccumulo': "passed serieRivAccumulo"
            },
            'contribuzione':
            {
                'dipendente':
                    "list of yearly voluntary contributions from dipendente"
                    "float",
                'datore':
                    "list of yearly contributions from datore"
                    "float",
                'tfr':
                    "list of yearly TFR contributions"
                    "float",
                'totale':
                    "sum of above contributions"
                    "float",
            },
            'deduzioni':
                "list of yearly deduzioni due to dipendente, float",
            'rivalutazione':
                "list of yearly revalution amounts of fondo pensione, float",
            'spese':
                "list of yearly expence amounts, float",
            'salario':
                "list of yearly salaries, float"
            'ultimoSalario': "last yearly salary, float"
            'montante':
                "list of yearly ammassed money on fondo pensione, float",
            'montanteErogato': "final net ammassed money amount, float",
            'rendita': "list of net yearly retirement wages, float",
            'tir':
            {
                'globale': "TIR, float",
                'dipendente':
                    "TIR but taking into account contributions from datore"
                    "and deduzioni due to dipendente"
                    "float"
            },
            'isc': "ISC, float"
        }
    """
    anni = len(serieRivSalario)

    retVal = {
        'tassi': {
            'inflazione': list(serieInflazione),
            'rivSalario': list(serieRivSalario),
            'rivAccumulo': list(serieRivAccumulo)
        },
        'contribuzione': {
            'tfr': [],
            'dipendente': [],
            'datore': [],
            'totale': []
        },
        'deduzioni': [],
        'rivalutazione': [0]*anni,
        'spese': [0]*anni,
        'salario': [],
        'ultimoSalario': 0.0,
        'montante': [0]*anni,
        'montanteErogato': 0.0,
        'rendita': [0]*35,
        'tir': {
            'globale': 0.0,
            'dipendente': 0.0
        },
        'isc': 0.0
    }

    descSalario = desc['salario']
    descDipendente = desc['dipendente']
    descFp = desc['fp']
    descPensione = desc['pensione']

    # Salario
    retVal['salario'] = \
        [descSalario['lordoAnnuo']*reduce(lambda x, y:x*(1+y),
                                          serieRivSalario[:i+1], 1)
            for i in range(anni)]
    retVal['salario'] = [round(x, 2) for x in retVal['salario']]

    ratioPrimoAnno = (12.0-descDipendente['inizioPiano'].month+1)/12.0
    ratioUltimoAnno = descDipendente['nascita'].month/12.0

    retVal['ultimoSalario'] = retVal['salario'][-1]
    retVal['salario'][0] = round(retVal['salario'][0]*ratioPrimoAnno, 2)
    retVal['salario'][-1] = round(retVal['salario'][-1]*ratioUltimoAnno, 2)

    # TFR
    retVal['contribuzione']['tfr'] = \
        [round(x*0.0691, 2) for x in retVal['salario']]

    # Contribuzione dipendente e datore di lavoro
    if descFp['base']['tipo'] == 'chiuso':
        contrib = {'dipendente': {}, 'datore': {}}
        fpBaseContrib = descFp['base']['accumulo']['contribuzione']
        contrib['dipendente']['valore'] = \
            descFp['accumulo']['contribuzione']['dipendente']['valore']
        if contrib['dipendente']['valore'] <= \
                fpBaseContrib['dipendente']['minimaPerContributoDatore']:
            contrib['dipendente']['base'] = \
                fpBaseContrib['dipendente']['base']['sottoMinima']
            contrib['datore']['valore'] = 0.0
        else:
            contrib['dipendente']['base'] = \
                fpBaseContrib['dipendente']['base']['sopraMinima']
            contrib['datore']['valore'] = fpBaseContrib['datore']['valore']
        contrib['datore']['base'] = fpBaseContrib['datore']['base']
    else:
        fpAccContribDip = descFp['accumulo']['contribuzione']['dipendente']
        contrib = {
            'dipendente': {
                'valore': fpAccContribDip['valore'],
                'base': 'lordo'
            },
            'datore': {
                'valore': 0.0,
                'base': 'lordo'
            }
        }

    for k in contrib:
        aliquota = contrib[k]['valore']
        if contrib[k]['base'] == 'lordo':
            base = retVal['salario']
        elif contrib[k]['base'] == 'minContratto':
            base = [descSalario['minContrattoMese'] * 13 *
                    reduce(lambda x, y:x*(1+y), serieRivSalario[:i+1], 1)
                    for i in range(anni)]
            base[0] = base[0]*ratioPrimoAnno
            base[-1] = base[-1]*ratioUltimoAnno
        retVal['contribuzione'][k] = [round(x*aliquota, 2) for x in base]

    # Contribuzione totale
    retVal['contribuzione']['totale'] = \
        [sum([retVal['contribuzione'][k][i] for k in retVal['contribuzione']
             if k != 'totale']) for i in range(anni)]

    # Deduzioni
    if descFp['base']['tipo'] == 'chiuso':
        retVal['deduzioni'] = \
            [retVal['contribuzione']['dipendente'][i] +
             retVal['contribuzione']['datore'][i] for i in range(anni)]
        retVal['deduzioni'] = [(x if x <= 5164.57 else 5164.57)
                               for x in retVal['deduzioni']]
        retVal['deduzioni'] = [getIrpef(retVal['salario'][i]) -
                               getIrpef(retVal['salario'][i] -
                               retVal['deduzioni'][i]) for i in range(anni)]
    else:
        retVal['deduzioni'] = [0] * anni

    # Spese, Montante & Rivalutazione
    montantePerfetto = 0.0  # -- Serve per il calcolo dello ISC
    for i in range(anni):
        # Rivalutazione del primo anno di ogni versamento annuale
        # Ipotesi e' che le contribuzioni siano versate trimestralmente
        rivTrimestre = [math.pow(1+serieRivAccumulo[j], 0.25*(3-j))
                        for j in range(4)]

        mese = descDipendente['inizioPiano'].month if i == 0 else \
            (descDipendente['nascita'].month if i == anni-1 else 1)
        ratioTrimestre = \
            [sum([(0 if j+1 < mese else 1) for j in range(12)][3*k:3*(k+1)])
             for k in range(4)]
        ratioTrimestre = [float(x)/sum(ratioTrimestre) for x in ratioTrimestre]
        rivalutazione = sum([ratioTrimestre[j]*rivTrimestre[j]
                             for j in range(4)])-1

        montanteAp = (0.0 if i == 0 else retVal['montante'][i-1])
        contribuzione = retVal['contribuzione']['totale'][i] - \
            descFp['accumulo']['spese']['fisse']

        retVal['rivalutazione'][i] = \
            round(montanteAp * serieRivAccumulo[i] +
                  contribuzione * rivalutazione, 2)
        retVal['montante'][i] = montanteAp + contribuzione + \
            retVal['rivalutazione'][i]

        imposta = round(retVal['rivalutazione'][i] *
                        descFp['accumulo']['spese']['imposta'], 2)
        if imposta < 0:
            imposta = 0
        oneri = round(retVal['montante'][i] *
                      descFp['accumulo']['spese']['variabili'], 2)

        retVal['spese'][i] = descFp['accumulo']['spese']['fisse'] + \
            imposta + oneri
        retVal['montante'][i] -= imposta + oneri

        # Aggiornamento andamento del fondo pensione perfetto
        # -- Necessario per ISC
        rivalutazioneFPPerfetto = \
            round(montantePerfetto * serieRivAccumulo[i] +
                  retVal['contribuzione']['totale'][i] * rivalutazione, 2)
        impostaFPPerfetto = \
            round(rivalutazioneFPPerfetto *
                  descFp['accumulo']['spese']['imposta'], 2)
        montantePerfetto += retVal['contribuzione']['totale'][i] + \
            rivalutazioneFPPerfetto - impostaFPPerfetto

    # Montante erogato
    aliquota = [0.15]*15 + [0.15-i*0.003 for i in range(1, 21)] + [0.09]*20

    nonDedotto = [retVal['contribuzione']['dipendente'][i] +
                  retVal['contribuzione']['datore'][i] - 5164.57
                  for i in range(anni)]
    nonDedotto = sum([(0.0 if x < 0 else x) for x in nonDedotto])

    dedotto = nonDedotto + \
        sum([(r if r >= 0 else 0) for r in retVal['rivalutazione']])
    imponibile = retVal['montante'][-1] - dedotto
    imposta = round(imponibile * aliquota[anni-1], 2)

    retVal['montanteErogato'] = retVal['montante'][-1] - imposta

    # Rendite
    sessoDip = desc['dipendente']['sesso']
    etaPens = descPensione['etaPensionamento']

    tabConv = descFp['rendita']['tabellaTassiConversione']
    if tabConv[sessoDip][str(etaPens)] is not None:
        renditaLorda = \
            round((retVal['montante'][-1] - imposta) *
                  tabConv[sessoDip][str(etaPens)], 2)
    else:
        raise errors.EtaPensionamentoNotFoundError(sessoDip, etaPens)
    retVal['rendita'][0] = \
        round(renditaLorda - renditaLorda *
              descFp['rendita']['spese']['variabili'] -
              descFp['rendita']['spese']['fisse'], 2)
    retVal['rendita'][1:] = \
        [round(retVal['rendita'][0] *
               math.pow(1+descFp['rendita']['rivalutazione'], i), 2)
            for i in range(1, len(retVal['rendita']))]

    # TIR (Tasso interno di rendimento) - Globale
    movs = [0] + retVal['contribuzione']['totale']
    movs[-1] -= retVal['montanteErogato']
    retVal['tir']['globale'] = round(TIR(movs), 6)

    # TIR (Tasso interno di rendimento) - Dipendente
    movs = [0] + \
        [retVal['contribuzione']['dipendente'][i] +
            retVal['contribuzione']['tfr'][i] -
            retVal['deduzioni'][i] for i in range(anni)]
    movs[-1] -= retVal['montanteErogato']
    retVal['tir']['dipendente'] = round(TIR(movs), 6)

    # ISC
    movs = [0] + retVal['contribuzione']['totale']
    movs[-1] -= montantePerfetto*(1-aliquota[anni-1])
    tirPerfetto = round(TIR(movs), 6)

    retVal['isc'] = tirPerfetto - retVal['tir']['globale']

    return retVal
