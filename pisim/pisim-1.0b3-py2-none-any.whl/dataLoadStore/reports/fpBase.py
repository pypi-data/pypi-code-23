# -*- coding: utf-8 -*-

"""I/O class for **reports, fondo pensione base** info.

Module's content
================

"""

from common import RepDescBaseDescIo
from ..fondoPensione import base


class RepFpBaseDescIo(RepDescBaseDescIo):
    """I/O class for **reports, fondo pensione base** descriptors."""

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        RepDescBaseDescIo.__init__(
            self, 'repFpBase',
            base.tableDef, base.tableTranslation, reportId)
