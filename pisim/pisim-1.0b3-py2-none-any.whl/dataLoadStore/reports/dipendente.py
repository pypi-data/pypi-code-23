# -*- coding: utf-8 -*-

"""I/O class for **reports, dipendente** info.

Module's content
================

"""

from common import RepDescBaseDescIo
from .. import dipendente


class RepDipendenteDescIo(RepDescBaseDescIo):
    """I/O class for **reports, dipendente** descriptors."""

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        RepDescBaseDescIo.__init__(
            self, 'repDipendente',
            dipendente.tableDef, dipendente.tableTranslation, reportId)
