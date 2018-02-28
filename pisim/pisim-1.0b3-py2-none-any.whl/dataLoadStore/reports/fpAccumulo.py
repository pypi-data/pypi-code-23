# -*- coding: utf-8 -*-

"""I/O class for **reports, fondo pensione accumulo** info.

Module's content
================

"""

from common import RepDescBaseDescIo
from ..fondoPensione import accumulo


class RepFpAccumuloDescIo(RepDescBaseDescIo):
    """I/O class for **reports, fondo pensione accumulo** descriptors."""

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        RepDescBaseDescIo.__init__(
            self, 'repFpAccumulo',
            accumulo.tableDef, accumulo.tableTranslation, reportId)
