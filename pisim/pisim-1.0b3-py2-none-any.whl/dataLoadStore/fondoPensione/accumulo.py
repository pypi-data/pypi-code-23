# -*- coding: utf-8 -*-

"""I/O class for **fondo pensione, accumulo** info.

Module's content
================

"""

import sqlite3
from .. import common

#: Table definition. See :py:class:`~.common.DescIo` for further details.
tableDef = '''
    name TEXT {},
    contribDip REAL NOT NULL,
    rivValore REAL NOT NULL,
    rivVariazione REAL NOT NULL,
    speseFisse REAL NOT NULL,
    speseVariabili REAL NOT NULL,
    speseImposta REAL NOT NULL
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
tableTranslation = {
    'contribDip': 'contribuzione.dipendente.valore',
    'rivValore': 'rivalutazione.valore',
    'rivVariazione': 'rivalutazione.variazione',
    'speseFisse': 'spese.fisse',
    'speseVariabili': 'spese.variabili',
    'speseImposta': 'spese.imposta',
}


class FpAccumuloDescIo(common.DescIo):
    """I/O class for **fondo pensione, accumulo** descriptors.

    Any instance of this class is given the reference (i.e. row id)
    of a fondo pensione base entry in DB. In that way, it's possible
    to manipulate the set of descriptors of accumulo associated to
    the fondo pensione itself.

    Despite other classes, this one subclasses :py:class:`.DescIo`
    instead the helper one :py:class:`.Model1DescIo`.
    This is because a different :py:meth:`_inidDb` method is needed.

    Other methods of the :py:class:`.DescIo` are redefined as well.

    Descriptor is a dictionary defined as follows::

        {
            'contribuzione':
            {
                'dipendente':
                {
                    'valore':
                        "amount of contribution from dipendente"+
                        "expressed as ratio with respect to"+
                        "'base' specified in the fpBase descriptor"+
                        "float"
                }
            }
            'rivalutazione':
            {
                'valore':
                    "actual average yearly performance of fondo pensione,"
                    "inflation apart"+
                    "float",
                'variazione':
                    "max yearly variation of fondo pensione increase"+
                    "with respect to average yearly performance"+
                    "specified above"+
                    "float"
            }
            'spese':
            {
                'fisse':
                    "yearly fixed expenses, absolute value, float",
                'variabili':
                    "yearly variable expenses,"+
                    "ratio with respect to amount ammassed every year,"+
                    "float",
                'imposta':
                    "yearly taxes,"+
                    "ratio with respect to amount ammassed every year,"+
                    "float",
            }
        }

    """

    def __init__(self, fpId):
        """Constructor.

        :param int fpId: id of a fondo pensione base entry in DB.
            All fondo pensione accumulo items this class' instance will
            manipulate will be related to such a fondo pensione.
        """
        common.DescIo.__init__(self, 'fpAccumulo', tableDef, tableTranslation)

        #: Fondo pensione base's DB id. Initiated in :py:meth:`.__init__`.
        self._fpId = fpId

    def _initDb(self):
        """DB initialization."""
        try:
            common.DescIo._conn.execute('''
                CREATE TABLE IF NOT EXISTS {}
                (descId INTEGER PRIMARY KEY,
                fpId INTEGER NOT NULL REFERENCES fpBase(descId)
                    ON DELETE CASCADE,
                {}, UNIQUE (fpId, name))'''.format(
                self._module, self._tableDef.format('NOT NULL')))
            common.DescIo._conn.execute('''
                CREATE INDEX IF NOT EXISTS {}Index ON {} (fpId)'''.format(
                self._module, self._module))
            common.DescIo._conn.commit()
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)

    def save(self, desc, serialized=False):
        """Accumulo's descriptor saving into db.

        This method is redefined here because the fondo pensione's id
        has to be added to desc before trying saving
        it to DB. Saving is done by actually calling
        :py:meth:`.DescIo.save`.

        Refer to :py:meth:`.DescIo.save` for parameters and
        return value description.
        """
        tmpDesc = dict(desc)
        tmpDesc['fpId'] = self._fpId
        return common.DescIo.save(self, tmpDesc, serialized)

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
                 ('SELECT descId, name '
                  'FROM {} where fpId=?').format(self._module),
                 (self._fpId,))]
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)
