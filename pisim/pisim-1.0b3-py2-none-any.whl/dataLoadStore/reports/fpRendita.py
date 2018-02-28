# -*- coding: utf-8 -*-

"""I/O class for **reports, fondo pensione rendita** info.

Module's content
================

"""

from common import RepDescBaseDescIo
from ..fondoPensione import rendita


class RepFpRenditaDescIo(RepDescBaseDescIo):
    """I/O class for **reports, fondo pensione rendita** descriptors."""

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        RepDescBaseDescIo.__init__(
            self, 'repFpRendita',
            rendita.tableDef, rendita.tableTranslation, reportId)
