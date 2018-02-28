# -*- coding: utf-8 -*-

"""Module computing macro-results of a given configuration.

Module's content
================

"""

from common import VAN1, getIrpef, VAN, TIR


def get(descs, pianoFp, pianoTfr):
    """Report computation.

    :param dict descs: configuration descriptors, defined the same as
        the input parameter of :py:func:`.fondoPensione.getPiano`.
    :param dict pianoFp: Output of :py:func:`.fondoPensione.getPiano`.
    :param dict pianoTfr: Output of :py:func:`tfr.getPiano`.
    :returns: The report. Its definition is the same as
        :py:class:`.RepResultsDescIo`.
    :rtype: dict
    """
    serieInflazione = pianoFp['tassi']['inflazione']
    anni = len(serieInflazione)

    ultimoSalarioLordoIrpef = pianoFp['ultimoSalario'] * (1-0.0919)
    tfrEquiv = pianoTfr['montanteErogato'] + \
        sum(pianoFp['contribuzione']['dipendente']) - \
        sum(pianoFp['deduzioni'])

    retVal = {
        'descs': descs,
        'tassi': {
            'inflazione': list(serieInflazione),
            'rivSalario': list(pianoFp['tassi']['rivSalario']),
            'rivFp': list(pianoFp['tassi']['rivAccumulo']),
        },
        'ultimoSalario': {
            'lordo': VAN1(pianoFp['ultimoSalario'], serieInflazione),
            'netto': VAN1(ultimoSalarioLordoIrpef -
                          getIrpef(ultimoSalarioLordoIrpef), serieInflazione),
        },
        'fp': {
            'primoAnno': {
                'contribuzione': {
                    'tfr': VAN1(pianoFp['contribuzione']['tfr'][0],
                                [serieInflazione[0]]),
                    'datore': VAN1(pianoFp['contribuzione']['datore'][0],
                                   [serieInflazione[0]]),
                    'dipendente':
                        VAN1(pianoFp['contribuzione']['dipendente'][0],
                             [serieInflazione[0]])
                },
                'deduzioni': VAN1(pianoFp['deduzioni'][0],
                                  [serieInflazione[0]]),
                'salario': VAN1(pianoFp['salario'][0], [serieInflazione[0]])
            },
            'accumulo': {
                'contribuzione': {
                    'tfr': VAN(pianoFp['contribuzione']['tfr'],
                               serieInflazione),
                    'dipendente': VAN(pianoFp['contribuzione']['dipendente'],
                                      serieInflazione),
                    'datore': VAN(pianoFp['contribuzione']['datore'],
                                  serieInflazione),
                    'deduzioni': VAN(pianoFp['deduzioni'], serieInflazione)
                },
                'montante': {
                    'finale': VAN1(pianoFp['montante'][-1], serieInflazione),
                    'erogato': VAN1(pianoFp['montanteErogato'],
                                    serieInflazione),
                },
                'tir': {
                    'globale': pianoFp['tir']['globale'],
                    'dipendente': pianoFp['tir']['dipendente']
                },
                'isc': pianoFp['isc']
            },
            'rendita': VAN1(pianoFp['rendita'][0], serieInflazione)
        },
        'tfr': {
            'accumulo': {
                'montante': {
                    'finale': VAN1(pianoTfr['montante'][-1], serieInflazione),
                    'erogato': VAN1(pianoTfr['montanteErogato'],
                                    serieInflazione)
                },
                'tir': {
                    'senzaContributi': pianoTfr['tir'],
                    'conContributiNoRiv': TIR(
                        [0] +
                        [pianoFp['contribuzione']['dipendente'][i] +
                            pianoTfr['contribuzione'][i]
                            for i in range(anni)] +
                        [-sum(pianoFp['contribuzione']['dipendente']) -
                            pianoTfr['montanteErogato']])
                },
                'isc': 0.0,
            },
            'rendita': {
                'durataAnni':
                    [i+1 for i in range(len(pianoFp['rendita']))
                        if sum(pianoFp['rendita'][:i+1]) <= tfrEquiv][-1]
            }
        },
        'pensioneInps': {
            'lorda': VAN1(descs['pensione']['tassoSostituzione'] *
                          pianoFp['ultimoSalario'], serieInflazione),
            'netta': VAN1(descs['pensione']['tassoSostituzione'] *
                          pianoFp['ultimoSalario'] -
                          getIrpef(0.63*pianoFp['ultimoSalario']),
                          serieInflazione)
        }
    }

    return retVal
