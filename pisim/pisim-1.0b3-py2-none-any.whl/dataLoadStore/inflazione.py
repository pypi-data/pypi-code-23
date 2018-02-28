# -*- coding: utf-8 -*-

"""I/O class for **inflazione** info.

Module's content
================

"""

import common

#: Table definition. See :py:class:`~.common.DescIo` for further details.
tableDef = '''
    name TEXT {},
    tassoMedio REAL NOT NULL,
    variazione REAL NOT NULL
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
#: None is provided here since table's column headers are the same as
#: descriptor's keys.
tableTranslation = {}


class InflazioneDescIo(common.Model1DescIo):
    """I/O class for **inflazione** descriptors.

    Descriptor is a dictionary defined as follows::

        {
            'tassoMedio': "average value, float",
            'variazione': "range of uniform dist. random variations, float"
        }
    """

    def __init__(self):
        """Constructor."""
        common.Model1DescIo.__init__(
            self, 'inflazione',
            tableDef, tableTranslation)
