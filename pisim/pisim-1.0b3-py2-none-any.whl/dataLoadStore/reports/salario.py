# -*- coding: utf-8 -*-

"""I/O class for **reports, salario** info.

Module's content
================

"""

from common import RepDescBaseDescIo
from .. import salario


class RepSalarioDescIo(RepDescBaseDescIo):
    """I/O class for **reports, salario** descriptors."""

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        RepDescBaseDescIo.__init__(
            self, 'repSalario',
            salario.tableDef, salario.tableTranslation, reportId)
