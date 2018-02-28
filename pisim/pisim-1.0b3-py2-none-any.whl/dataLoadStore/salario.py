# -*- coding: utf-8 -*-

"""I/O class for **salario** info.

Module's content
================

"""

import common

#: Table definition. See :py:class:`~.common.DescIo` for further details.
tableDef = '''
    name TEXT {},
    lordoAnnuo REAL NOT NULL,
    minContrattoMese REAL NOT NULL,
    rivValore REAL NOT NULL,
    rivFrequenza INTEGER NOT NULL
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
tableTranslation = {
    'lordoAnnuo': 'lordoAnnuo',
    'minContrattoMese': 'minContrattoMese',
    'rivValore': 'rivalutazione.valore',
    'rivFrequenza': 'rivalutazione.frequenza',
}


class SalarioDescIo(common.Model1DescIo):
    """I/O class for **salario** descriptors.

    Descriptor is a dictionary defined as follows::

        {
            'lordoAnnuo': "starting gross yearly salary",
            'minContrattoMese': "min monthly salary level",
            'rivalutazione':
            {
                'valore': "avg. yearly salary increase, inflation apart",
                'frequenza': "yearly frequence at which increase is applied"
            }
        }
    """

    def __init__(self):
        """Constructor."""
        common.Model1DescIo.__init__(
            self, 'salario',
            tableDef, tableTranslation)
