# -*- coding: utf-8 -*-

"""I/O class for **report** info.

Module's content
================

"""

import sqlite3
from .. import common
import results
import dipendente
import inflazione
import salario
import pensione
import fpBase
import fpAccumulo
import fpRendita
import string

#: Table definition. See :py:class:`~.common.DescIo` for further details.
tableDef = '''
    name TEXT {},
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
#: None is provided here since table's column headers are the same as
#: descriptor's keys.
tableTranslation = {}


class ReportsDescIo(common.DescIo):
    """I/O class for **reports** descriptors.

    This is the solely class to be used to manipulate reports' descriptors.
    Other classes defined in the same ``reports`` package are internally
    used by this one.

    Despite other classes, this one subclasses :py:class:`.DescIo`
    instead the helper one :py:class:`.Model1DescIo`.
    This is because a different :py:meth:`_inidDb` method is needed.

    Other methods of the :py:class:`.DescIo` are redefined as well.

    Since a report descriptors is a collection of sub-descriptors, there's
    no direct mapping between a report DB table definition and its
    descriptors. Instead a report descriptor is defined as follows::

        {
            'name': "report name",
            'results':
            {
                'best':
                {
                    # best scenario results
                    "keys same as produced by bestWorstScenario()"
                    "values being dictionaries themselves:"
                    {
                        'average': 'average value for the key',
                        'confInt': 'confidence interval for the key'
                    }
                },
                'worst': { "same as 'best' but for worst scenario" },
                'normal': { "same as 'best' but for normal/average scenario" }
            }
            'dipendente':
            {
                'name': "descriptive name of the sub-descriptor",
                DipendenteDescIo descriptor
            },
            'inflazione':
            {
                'name': "descriptive name of the sub-descriptor",
                InflazioneDescIo descriptor
            },
            'salario':
            {
                'name': "descriptive name of the sub-descriptor",
                SalarioDescIo descriptor
            },
            'pensione':
            {
                'name': "descriptive name of the sub-descriptor",
                PensioneDescIo descriptor
            },
            'fp':
            {
                'base':
                {
                    'name': "descriptive name of the sub-descriptor",
                    FpBaseDescIo descriptor
                },
                'accumulo':
                {
                    'name': "descriptive name of the sub-descriptor",
                    FpAccumuloDescIo descriptor
                },
                'rendita':
                {
                    'name': "descriptive name of the sub-descriptor",
                    FpRenditaDescIo descriptor
                },
            }
        }

    Links to the methods/classes mentioned above:

    * :py:func:`.bestWorstScenario`
    * Dipendente descriptor format: :py:class:`.DipendenteDescIo`
    * Inflazione descriptor format: :py:class:`.InflazioneDescIo`
    * Salario descriptor format: :py:class:`.SalarioDescIo`
    * Pensione descriptor format: :py:class:`.PensioneDescIo`
    * Fondo pensione, base descriptor format: :py:class:`.FpBaseDescIo`
    * Fondo pensione, accumulo descriptor format: :py:class:`.FpAccumuloDescIo`
    * Fondo pensione, rendita descriptor format: :py:class:`.FpRenditaDescIo`
    """

    def __init__(self):
        """Constructor."""
        common.DescIo.__init__(self, 'reports', tableDef, tableTranslation)

    def _initDb(self):
        """DB initialization."""
        try:
            common.DescIo._conn.execute(
                ("CREATE TABLE IF NOT EXISTS reports "
                 "(descId INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)"))
            common.DescIo._conn.commit()
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)

    def load(self, reportId, deserialized=True):
        """Descriptor saving into DB.

        This method is redefined here because this class perfomrs
        more complex ``SELECT`` operations than those provided by
        the base class. Namely several tables are queried here
        since the returned descriptor is the union of several
        sub-descriptors, each one stored by it own in a DB table.

        Refer to :py:meth:`.DescIo.load` for parameters and
        return value description.
        """
        desc = {}

        tmpDesc = common.DescIo.load(self, reportId)
        desc['name'] = tmpDesc['name']

        for resultDesc in results.RepResultsDescIo(reportId).load():
            if resultDesc['scenario'] == 0:
                k1 = 'worst'
            elif resultDesc['scenario'] == 1:
                k1 = 'best'
            elif resultDesc['scenario'] == 2:
                k1 = 'normal'
            k2 = 'average' if resultDesc['averages'] else 'confInt'
            desc.update(
                {'results.{}.{}.{}'.format(k1, k3, k2): resultDesc[k3]
                 for k3 in resultDesc if k3 not in ['scenarios', 'averages']})

        tmpDesc = dipendente.RepDipendenteDescIo(reportId).load()
        desc.update({'dipendente.{}'.format(k): tmpDesc[k] for k in tmpDesc})

        tmpDesc = inflazione.RepInflazioneDescIo(reportId).load()
        desc.update({'inflazione.{}'.format(k): tmpDesc[k] for k in tmpDesc})

        tmpDesc = salario.RepSalarioDescIo(reportId).load()
        desc.update({'salario.{}'.format(k): tmpDesc[k] for k in tmpDesc})

        tmpDesc = pensione.RepPensioneDescIo(reportId).load()
        desc.update({'pensione.{}'.format(k): tmpDesc[k] for k in tmpDesc})

        tmpDesc = fpBase.RepFpBaseDescIo(reportId).load()
        desc.update({'fp.base.{}'.format(k): tmpDesc[k] for k in tmpDesc})

        tmpDesc = fpAccumulo.RepFpAccumuloDescIo(reportId).load()
        desc.update({'fp.accumulo.{}'.format(k): tmpDesc[k] for k in tmpDesc})

        tmpDesc = fpRendita.RepFpRenditaDescIo(reportId).load()
        desc.update({'fp.rendita.{}'.format(k): tmpDesc[k] for k in tmpDesc})

        return (common.DescIo.deserializeDesc(desc) if deserialized else desc)

    def save(self, desc, serialized=False):
        """Descriptor saving into db.

        This method is redefined here for the same reason as
        :py:meth:`load` has been redefined.

        Refer to :py:meth:`.DescIo.save` for parameters and
        return value description.
        """
        reportId = common.DescIo.save(
            self,
            {'name': desc['name'], 'descId': desc.get('descId', None)},
            False)

        inDesc = common.DescIo.deserializeDesc(desc) if serialized else desc

        for k1 in ['best', 'worst', 'normal']:
            for k2 in ['average', 'confInt']:
                tmpDesc = {}
                if k1 == 'worst':
                    tmpDesc['scenario'] = 0
                elif k1 == 'best':
                    tmpDesc['scenario'] = 1
                elif k1 == 'normal':
                    tmpDesc['scenario'] = 2
                tmpDesc['averages'] = (k2 == 'average')
                resTmpDesc = common.DescIo.serializeDesc(inDesc['results'][k1])
                for k3 in [k for k in resTmpDesc if k2 in k]:
                    tmpDesc[k3[:string.rfind(k3, '.')]] = resTmpDesc[k3]
                results.RepResultsDescIo(reportId).save(tmpDesc, True)

        dipendente.RepDipendenteDescIo(reportId).save(
            inDesc['dipendente'], False)
        inflazione.RepInflazioneDescIo(reportId).save(
            inDesc['inflazione'], False)
        salario.RepSalarioDescIo(reportId).save(inDesc['salario'], False)
        pensione.RepPensioneDescIo(reportId).save(inDesc['pensione'], False)
        fpBase.RepFpBaseDescIo(reportId).save(inDesc['fp']['base'], False)
        fpAccumulo.RepFpAccumuloDescIo(reportId).save(
            inDesc['fp']['accumulo'], False)
        fpRendita.RepFpRenditaDescIo(reportId).save(
            inDesc['fp']['rendita'], False)

        return reportId

    def rename(self, reportId, newName):
        """Change the name of the report DB entry.

        This is a new method, not defined in the base class,
        because the renaming operations on other descriptors can be
        performed by the :py:meth:`.DescIo.save` method.

        :param int reportId: report id whose name has to be changed.
        :param str newName: new report name.
        """
        try:
            common.DescIo._conn.execute('''
                UPDATE {} SET name=? WHERE descId=?
                '''.format(self._module), (newName, reportId))
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)
