# -*- coding: utf-8 -*-

"""Module implementing the computation of the development of the TFR.

Module's content
================

"""

from common import getIrpef, TIR


def getPiano(desc, serieInflazione, serieRivSalario):
    """Compute tehe year-over-year develop of TFR.

    :param dict desc:
        dictionary containing all configuration descriptors.
        For its format refer to :py:func:`.fondoPensione.getPiano`.
    :param list(float) serieInflazione:
        list of inflation indexes.
    :param list(float) serieRivSalario:
        list of yearly salary revalutation indexes, inflation apart.
    :returns: the dictionary containing the TFR elaboration results.
    :rtype: dict

    The returned descriptor is defined as follows::

        {
            'tassi':
            {
                'inflazione': "passed serieInflazione",
                'rivSalario': "passed serieRivSalario",
            },
            'contribuzione':
                "list of yearly TFR contributions"
                "float",
            'rivalutazione':
                "list of yearly revalution amounts of TFR, float",
            'salario':
                "list of yearly salaries, float"
            'montante': "list of yearly ammassed money on TFR, float",
            'montanteErogato': "final net ammassed money amount, float",
            'tir': "TIR, float"
        }
    """
    anni = len(serieRivSalario)

    retVal = {
        'tassi': {
            'inflazione': list(serieInflazione),
            'rivSalario': list(serieRivSalario)
        },
        'contribuzione': [],
        'rivalutazione': [0]*anni,
        'salario': [],
        'montante': [0]*anni,
        'montanteErogato': 0.0,
        'tir': 0.0
    }

    salario = desc['salario']

    # Salario
    retVal['salario'] = \
        [salario['lordoAnnuo'] *
         reduce(lambda x, y:x*(1+y), serieRivSalario[:i+1], 1)
         for i in range(anni)]
    retVal['salario'] = [round(x, 2) for x in retVal['salario']]

    # Quote TFR
    retVal['contribuzione'] = [round(x*0.0691, 2) for x in retVal['salario']]

    # Montante & Rivalutazione
    for i in range(anni):
        retVal['montante'][i] = (0.0 if i == 0 else retVal['montante'][i-1])
        retVal['montante'][i] += retVal['contribuzione'][i]
        retVal['rivalutazione'][i] = \
            retVal['montante'][i] * \
            (0.015 + 0.75*serieInflazione[i]) * (1-0.17)
        retVal['montante'][i] += retVal['rivalutazione'][i]

    # Montante erogato
    imponibile = sum(retVal['contribuzione'])/anni*12
    aliquota = getIrpef(imponibile)/imponibile

    retVal['montanteErogato'] = \
        round(retVal['montante'][-1] -
              (retVal['montante'][-1] -
              sum(retVal['rivalutazione']))*aliquota, 2)

    # TIR
    coeffs = [0] + retVal['contribuzione']
    coeffs[-1] -= retVal['montanteErogato']
    retVal['tir'] = TIR(coeffs)

    return retVal
