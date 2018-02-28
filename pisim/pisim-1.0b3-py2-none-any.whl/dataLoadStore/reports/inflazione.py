# -*- coding: utf-8 -*-

"""I/O class for **reports, inflazione** info.

Module's content
================

"""

from common import RepDescBaseDescIo
from .. import inflazione


class RepInflazioneDescIo(RepDescBaseDescIo):
    """I/O class for **reports, inflazione** descriptors."""

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        RepDescBaseDescIo.__init__(
            self, 'repInflazione',
            inflazione.tableDef, inflazione.tableTranslation, reportId)
