# -*- coding: utf-8 -*-

"""I/O class for **reports, pensione** info.

Module's content
================

"""

from common import RepDescBaseDescIo
from .. import pensione


class RepPensioneDescIo(RepDescBaseDescIo):
    """I/O class for **reports, pensione** descriptors."""

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        RepDescBaseDescIo.__init__(
            self, 'repPensione',
            pensione.tableDef, pensione.tableTranslation, reportId)
