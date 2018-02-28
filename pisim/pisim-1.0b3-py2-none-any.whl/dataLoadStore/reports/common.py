# -*- coding: utf-8 -*-

"""Base I/O class for many report-related info.

Module's content
================

"""

import sqlite3
from .. import common


class RepDescBaseDescIo(common.DescIo):
    """Base I/O class for many report-related descriptors.

    Any instance of this class is given the reference (i.e. report id)
    of a report in DB. In that way, it's possible
    to manipulate the descriptor associated to
    the report itself. This is because *only one record
    is supposed being associated to a report*.

    Despite other classes, this one subclasses :py:class:`.DescIo`
    instead the helper one :py:class:`.Model1DescIo`.
    This is because a different :py:meth:`_inidDb` method is needed.

    Other methods of the :py:class:`.DescIo` are redefined as well.

    Subclasses of this are internally used by :py:class:`.ReportsDescIo`.
    """

    def __init__(self, moduleName, tableDef, tableTranslation, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        common.DescIo.__init__(
            self, moduleName, tableDef, tableTranslation)

        #: Id of the report to which descriptor's row is associated.
        self._reportId = reportId

    def _initDb(self):
        """DB initialization."""
        try:
            common.DescIo._conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS {}
                (descId INTEGER PRIMARY KEY,
                reportId INTEGER UNIQUE NOT NULL
                    REFERENCES reports(descId) ON DELETE CASCADE,
                {})'''.format(self._module, self._tableDef.format('')))
            common.DescIo._conn.execute('''
                CREATE INDEX IF NOT EXISTS {}Index ON {} (reportId)
                '''.format(self._module, self._module))
            common.DescIo._conn.commit()
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)

    def load(self):
        """Descriptor loading from db.

        This method is redefined here because:

        * No id is to be provided, since only one record
          is associated to a report (id's stores in :py:data:`_reportId`).
        * Only the record associated to a report has to be
          retrieved.
        """
        desc = {}

        try:
            crs = common.DescIo._conn.cursor()
            crs.execute(
                'SELECT * FROM {} WHERE reportId=?'.format(
                    self._module), (self._reportId,))

            row = crs.fetchone()
            for k in row.keys():
                try:
                    desc[self._tableDescTranslation[k]] = row[k]
                except KeyError:
                    desc[k] = row[k]
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)

        # Note: no deserialization is done. Left to the calling procedure
        return desc

    def save(self, desc, serialized=False):
        """Descriptor saving into db.

        This method is redefined here because the report's id has to be added
        to desc before trying saving it to DB. Saving is done by actually
        calling :py:meth:`.DescIo.save`.

        Refer to :py:meth:`.DescIo.save` for parameters and
        return value description.
        """
        tmpDesc = dict(desc)
        tmpDesc['reportId'] = self._reportId
        common.DescIo.save(self, tmpDesc, serialized)
