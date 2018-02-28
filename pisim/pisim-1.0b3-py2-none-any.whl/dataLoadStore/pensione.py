# -*- coding: utf-8 -*-

"""I/O class for **pensione** info.

Module's content
================

"""

import common

#: Table definition. See :py:class:`~.common.DescIo` for further details.
tableDef = '''
    name TEXT {},
    etaPensionamento INTEGER NOT NULL,
    tassoSostituzione REAL NOT NULL
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
#: None is provided here since table's column headers are the same as
#: descriptor's keys.
tableTranslation = {}


class PensioneDescIo(common.Model1DescIo):
    """I/O class for **pensione** descriptors.

    Descriptor is a dictionary defined as follows::

        {
            'etaPensionamento': "age or retirement, int",
            'tassoSostituzione': "ret. salary vs. last salary ratio, float"
        }
    """

    def __init__(self):
        """Constructor."""
        common.Model1DescIo.__init__(
            self, 'pensione',
            tableDef, tableTranslation)
