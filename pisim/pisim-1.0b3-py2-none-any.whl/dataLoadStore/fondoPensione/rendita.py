# -*- coding: utf-8 -*-

"""I/O class for **fondo pensione, rendita** info.

Module's content
================

"""

import sqlite3
from .. import common

#: Table definition. See :py:class:`~.common.DescIo` for further details.
tableDef = \
    'name TEXT {}, ' + \
    ', '.join(['tcM{} REAL'.format(i) for i in range(50, 71)]) + ', ' +\
    ', '.join(['tcF{} REAL'.format(i) for i in range(50, 71)]) + ', ' + '''
    speseFisse REAL NOT NULL,
    speseVariabili REAL NOT NULL,
    rivalutazione REAL NOT NULL'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
tableTranslation = dict(
    [('speseFisse', 'spese.fisse'),
        ('speseVariabili', 'spese.variabili'),
        ('rivalutazione', 'rivalutazione')] +
    [('tcM{}'.format(i), 'tabellaTassiConversione.m.{}'.format(i))
        for i in range(50, 71)] +
    [('tcF{}'.format(i), 'tabellaTassiConversione.f.{}'.format(i))
        for i in range(50, 71)]
)


class FpRenditaDescIo(common.DescIo):
    """I/O class for **fondo pensione, rendita** descriptors.

    Any instance of this class is given the reference (i.e. row id)
    of a fondo pensione base entry in DB. In that way, it's possible
    to manipulate the set of descriptors of rendita associated to
    the fondo pensione itself.

    Despite other classes, this one subclasses :py:class:`.DescIo`
    instead the helper one :py:class:`.Model1DescIo`.
    This is because a different :py:meth:`_inidDb` method is needed.

    Other methods of the :py:class:`.DescIo` are redefined as well.

    Descriptor is a dictionary defined as follows::

        {
            'tabellaTassiConversione':
            {
                'm':
                {
                    # Sequence of keys 'i', with i being integer
                    # in the range [50,71],
                    # Each one holding a float value
                    # representing the conversion from
                    # the total amount ammassed at the end of
                    # fondo pensione accumulo phase
                    # (with i being the retirement age)
                    # to the retirement yearly wage, for males.
                }
                'f':
                {
                    # Same as 'm' for females.
                }
            }
            'spese':
            {
                'fisse':
                    "yearly fixed expenses, absolute value, float",
                'variabili':
                    "yearly variable expenses,"+
                    "ratio with respect to yearly wage,"+
                    "float",
            }
        }
    """

    def __init__(self, fpId):
        """Constructor.

        :param int fpId: id of a fondo pensione base entry in DB.
            All fondo pensione rendita items this class' instance will
            manipulate will be related to such a fondo pensione.
        """
        common.DescIo.__init__(self, 'fpRendita', tableDef, tableTranslation)

        #: Fondo pensione base's DB id. Initiated in :py:meth:`.__init__`.
        self._fpId = fpId

    def _initDb(self):
        """DB initialization."""
        try:
            common.DescIo._conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS {}
                (descId INTEGER PRIMARY KEY,
                fpId INTEGER NOT NULL REFERENCES fpBase(descId)
                    ON DELETE CASCADE,
                {}, UNIQUE (fpId, name))'''.format(
                    self._module, self._tableDef.format('NOT NULL')))
            common.DescIo._conn.execute(
                '''CREATE INDEX IF NOT EXISTS {}Index ON {} (fpId)'''.format(
                    self._module, self._module))
            common.DescIo._conn.commit()
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)

    def save(self, desc, serialized=False):
        """Rendita's descriptor saving into db.

        This method is redefined here because the fondo pensione's id
        has to be added to desc before trying saving
        it to DB. Saving is done by actually calling
        :py:meth:`.DescIo.save`.

        Refer to :py:meth:`.DescIo.save` for parameters and
        return value description.
        """
        tmpDesc = dict(desc)
        tmpDesc['fpId'] = self._fpId
        common.DescIo.save(self, tmpDesc, serialized)

    def list(self):
        """List of saved descriptors retrieval.

        This method is redefined here because DB lookup is different from
        the one implemented in :py:meth:`.DescIo.list` in that
        only a subset of stored descriptors have to be retrieved,
        namely those referring to the fondo pensione id
        :py:data:`_fpId` have to be retrieved.

        Refer to :py:meth:`.descIo.list` for info about return value
        format.
        """
        try:
            return \
                [{'descId': r['descId'], 'name': r['name']}
                 for r in common.DescIo._conn.execute(
                    'SELECT descId, name FROM {} where fpId=?'.format(
                        self._module),
                    (self._fpId,))]
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)
