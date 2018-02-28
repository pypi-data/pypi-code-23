# -*- coding: utf-8 -*-

"""Initialization code for DB's tables.

Code here is different from that in :py:meth:`.DescIo._initDb`.
In the latter, DB Initialization consists in table creation.
Here instead it's about storing kwnown descriptors in some tables.

Module's content
================

"""

from fondoPensione.base import FpBaseDescIo
from fondoPensione.accumulo import FpAccumuloDescIo
from fondoPensione.rendita import FpRenditaDescIo


def run():
    """Check if db has some default descriptors. If not so, add them."""
    # fpBase default descriptors
    fpBaseDescsList = [
        {
            'name': 'cometa',
            'tipo': 'chiuso',
            'accumulo.contribuzione.dipendente.minimaPerContributoDatore':
                0.012,
            'accumulo.contribuzione.dipendente.base.sottoMinima':
                'minContratto',
            'accumulo.contribuzione.dipendente.base.sopraMinima': 'lordo',
            'accumulo.contribuzione.datore.base': 'minContratto',
            'accumulo.contribuzione.datore.valore': 0.02
        },
    ]

    # fpAccumulo default descriptors
    fpAccumuloDescsList = {
        fpBaseDescsList[0]['name']: [
            {
                'name': 'crescita-2018',
                'contribuzione.dipendente.valore': 0.08,
                'rivalutazione.valore': 0.02,
                'rivalutazione.variazione': 0.17,
                'spese.fisse': 17.0,
                'spese.variabili': 0.008,
                'spese.imposta': 0.16
            },
        ]
    }

    # fpRendita default descriptors
    fpRenditaDescsList = {
        fpBaseDescsList[0]['name']: [
            {
                'name': 'immediata-tc0-2018',
                'tabellaTassiConversione.m.50': 0.0278977,
                'tabellaTassiConversione.m.51': 0.0286710,
                'tabellaTassiConversione.m.52': 0.0294859,
                'tabellaTassiConversione.m.53': 0.0303458,
                'tabellaTassiConversione.m.54': 0.0312535,
                'tabellaTassiConversione.m.55': 0.0322129,
                'tabellaTassiConversione.m.56': 0.0332283,
                'tabellaTassiConversione.m.57': 0.0343050,
                'tabellaTassiConversione.m.58': 0.0354487,
                'tabellaTassiConversione.m.59': 0.0366655,
                'tabellaTassiConversione.m.60': 0.0379613,
                'tabellaTassiConversione.m.61': 0.0393413,
                'tabellaTassiConversione.m.62': 0.0408095,
                'tabellaTassiConversione.m.63': 0.0423741,
                'tabellaTassiConversione.m.64': 0.0440447,
                'tabellaTassiConversione.m.65': 0.0458308,
                'tabellaTassiConversione.m.66': 0.0477418,
                'tabellaTassiConversione.m.67': 0.0497896,
                'tabellaTassiConversione.m.68': 0.0519880,
                'tabellaTassiConversione.m.69': 0.0543523,
                'tabellaTassiConversione.m.70': 0.0568971,
                'tabellaTassiConversione.f.50': 0.0251047,
                'tabellaTassiConversione.f.51': 0.0257319,
                'tabellaTassiConversione.f.52': 0.0263900,
                'tabellaTassiConversione.f.53': 0.0270812,
                'tabellaTassiConversione.f.54': 0.0278078,
                'tabellaTassiConversione.f.55': 0.0285730,
                'tabellaTassiConversione.f.56': 0.0293799,
                'tabellaTassiConversione.f.57': 0.0302325,
                'tabellaTassiConversione.f.58': 0.0311349,
                'tabellaTassiConversione.f.59': 0.0320916,
                'tabellaTassiConversione.f.60': 0.0331071,
                'tabellaTassiConversione.f.61': 0.0341862,
                'tabellaTassiConversione.f.62': 0.0353326,
                'tabellaTassiConversione.f.63': 0.0365510,
                'tabellaTassiConversione.f.64': 0.0378487,
                'tabellaTassiConversione.f.65': 0.0392343,
                'tabellaTassiConversione.f.66': 0.0407088,
                'tabellaTassiConversione.f.67': 0.0422912,
                'tabellaTassiConversione.f.68': 0.0439899,
                'tabellaTassiConversione.f.69': 0.0458165,
                'tabellaTassiConversione.f.70': 0.0477836,
                'spese.fisse': 0,
                'spese.variabili': 0.0125,
                'rivalutazione': 0.025
            },
        ]
    }

    for fpBaseDesc in fpBaseDescsList:
        fpBaseName = fpBaseDesc['name']
        fpBaseList = FpBaseDescIo().list()

        # Checking if a fbBase desc exists with kwnown name
        if fpBaseName not in [d['name'] for d in fpBaseList]:
            # No -- Saving it
            fpId = FpBaseDescIo().save(fpBaseDesc, True)
        else:
            # Yes -- Retrieving its descId
            fpId = [d['descId'] for d in fpBaseList if d['name'] ==
                    fpBaseName][0]

        fpAccumuloIo = FpAccumuloDescIo(fpId)
        fpRenditaIo = FpRenditaDescIo(fpId)

        # Store fpAccumulo descs if they're not already in database
        fpAccumuloList = fpAccumuloIo.list()
        for fpAccumuloDesc in [e for e in fpAccumuloDescsList[fpBaseName]
                               if e['name'] not in
                               [d['name'] for d in fpAccumuloList]]:
            fpAccumuloIo.save(fpAccumuloDesc, True)

        # Store fpRendita descs if they're not already in database
        fpRenditaList = fpRenditaIo.list()
        for fpRenditaDesc in [e for e in fpRenditaDescsList[fpBaseName]
                              if e['name'] not in [d['name']
                              for d in fpRenditaList]]:
            fpRenditaIo.save(fpRenditaDesc, True)
