# -*- coding: utf-8 -*-

"""I/O class for **dipendente** info.

Module's content
================

"""

import common

#: Table definition. See :py:class:`.DescIo` for further details.
tableDef = '''
    name TEXT {},
    nascita date NOT NULL ,
    sesso TEXT NOT NULL ,
    inizioPiano date NOT NULL
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
#: None is provided here since table's column headers are the same as
#: descriptor's keys.
tableTranslation = {}


class DipendenteDescIo(common.Model1DescIo):
    """I/O class for **dipendente** descriptors.

    Descriptor is a dictionary defined as follows::

        {
            'nascita': "birth date, datetime.date instance",
            'sesso': "sex, in ['m', 'f']",
            'inizioPiano': "plan starting date, datetime.date instance"
        }
    """

    def __init__(self):
        """Constructor."""
        common.Model1DescIo.__init__(
            self, 'dipendente',
            tableDef, tableTranslation)
