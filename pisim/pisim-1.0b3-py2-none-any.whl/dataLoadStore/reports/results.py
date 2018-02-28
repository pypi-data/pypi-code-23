# -*- coding: utf-8 -*-

"""I/O class for **reports, results** info.

Module's content
================

"""

import sqlite3
from .. import common

#: Table definition. See :py:class:`~.DescIo` for further details.
tableDef = '''
    scenario INTEGER NOT NULL,
    averages INTEGER NOT NULL,
    fpRendita REAL NOT NULL,
    fpDeduzioni REAL NOT NULL,
    fpContribDipendente REAL NOT NULL,
    fpContribDatore REAL NOT NULL,
    fpAccTfr REAL NOT NULL,
    fpAccIsc REAL NOT NULL,
    fpAccMontanteErogato REAL NOT NULL,
    fpAccMontanteFinale REAL NOT NULL,
    fpAccTirDip REAL NOT NULL,
    fpAccTirGlob REAL NOT NULL,
    fpPAnnoContribDipendente REAL NOT NULL,
    fpPAnnoContribDatore REAL NOT NULL,
    fpPAnnoContribTfr REAL NOT NULL,
    fpPAnnoDeduzioni REAL NOT NULL,
    fpPAnnoSalario REAL NOT NULL,
    pensNetta REAL NOT NULL,
    pensLorda REAL NOT NULL,
    uAnnoSalarioLordo REAL NOT NULL,
    uAnnoSalarioNetto REAL NOT NULL,
    tfrRenditaDurata REAL NOT NULL,
    tfrAccIsc REAL NOT NULL,
    tfrAccMontanteErogato REAL NOT NULL,
    tfrAccMontanteFinale REAL NOT NULL,
    tfrAccTirCContributi REAL NOT NULL,
    tfrAccTirSContributi REAL NOT NULL
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.DescIo` for further details.
tableTranslation = {
    'fpRendita': 'fp.rendita',
    'fpDeduzioni': 'fp.accumulo.contribuzione.deduzioni',
    'fpContribDipendente': 'fp.accumulo.contribuzione.dipendente',
    'fpContribDatore': 'fp.accumulo.contribuzione.datore',
    'fpAccTfr': 'fp.accumulo.contribuzione.tfr',
    'fpAccIsc': 'fp.accumulo.isc',
    'fpAccMontanteErogato': 'fp.accumulo.montante.erogato',
    'fpAccMontanteFinale': 'fp.accumulo.montante.finale',
    'fpAccTirDip': 'fp.accumulo.tir.dipendente',
    'fpAccTirGlob': 'fp.accumulo.tir.globale',
    'fpPAnnoContribDipendente': 'fp.primoAnno.contribuzione.dipendente',
    'fpPAnnoContribDatore': 'fp.primoAnno.contribuzione.datore',
    'fpPAnnoContribTfr': 'fp.primoAnno.contribuzione.tfr',
    'fpPAnnoDeduzioni': 'fp.primoAnno.deduzioni',
    'fpPAnnoSalario': 'fp.primoAnno.salario',
    'pensNetta': 'pensioneInps.netta',
    'pensLorda': 'pensioneInps.lorda',
    'uAnnoSalarioLordo': 'ultimoSalario.lordo',
    'uAnnoSalarioNetto': 'ultimoSalario.netto',
    'tfrRenditaDurata': 'tfr.rendita.durataAnni',
    'tfrAccIsc': 'tfr.accumulo.isc',
    'tfrAccMontanteErogato': 'tfr.accumulo.montante.erogato',
    'tfrAccMontanteFinale': 'tfr.accumulo.montante.finale',
    'tfrAccTirCContributi': 'tfr.accumulo.tir.conContributiNoRiv',
    'tfrAccTirSContributi': 'tfr.accumulo.tir.senzaContributi',
}


class RepResultsDescIo(common.DescIo):
    """I/O class for **reports, results** descriptors.

    Any instance of this class is given the reference (i.e. report id)
    of a report in DB. In that way, it's possible
    to manipulate the descriptor associated to
    the report itself. Notice in fact that *only one record
    is associated to a report*.

    Despite other classes, this one subclasses :py:class:`.DescIo`
    instead the helper one :py:class:`.Model1DescIo`.
    This is because a different :py:meth:`_inidDb` method is needed.

    Other methods of the :py:class:`.DescIo` are redefined as well.

    Descriptor is a dictionary defined as follows::

        # All voices are purged from inflation
        {
            'fp':
            {
                # Voices composing the contribution to fondo pensione,
                # first year
                'primoAnno':
                {
                    'contribuzione':
                    {
                        'dipendente': "contribution from dipendente, float"
                        'datore': "contribution from datore, float",
                        'tfr': "tfr, float"
                    },
                    'deduzioni': "deduzioni due to dipendente, float",
                    'salario': "total salary, float"
                },
                # Results of the fondo pensione, accumulo phase
                'accumulo':
                {
                    # Total contribution components
                    'contribuzione':
                    {
                        'dipendente': "From dipendente, float",
                        'deduzioni': "Deduzioni due to dipendente, float",
                        'datore': "From datore, float",
                        'tfr': "From TFR, float"
                    },
                    # Total ammassed at the end of the phase
                    'montante':
                    {
                        'finale': "Gross, float",
                        'erogato': "Net (after taxes), float"
                    },
                    # Tasso Interno di Rendimento
                    'tir':
                    {
                        'globale':
                            "Taking into accont"
                            "only contribution from dipendente"
                            "float",
                        'dipendente':
                            "Considering other virtual positive contributions"
                            "i.e. from datore and deduzioni"
                            "float"
                    },
                    'isc': "Indice Sintetico di Costo, float"
                },
                'rendita': "Final net retirement wage, float"
            },
            # Last salary
            'ultimoSalario':
            {
                'lordo': "Gross, float",
                'netto': "Net, float"
            },
            # Public retirement wage
            'pensioneInps':
            {
                'lorda': "Gross, float",
                'netta': "Net, float"
            },
            # Performance of the Trattamento di Fine Rapporto
            # in case of no fondo pensione
            'tfr':
            {
                # Accumulo phase
                'accumulo':
                {
                    # Total ammassed
                    'montante':
                    {
                        'finale': "Gross, float",
                        'erogato': "Net, float"
                    },
                    # Tasso Interno di Rendimento
                    'tir':
                    {
                        'senzaContributi':
                            "With no other contributions, float",
                        'conContributiNoRiv':
                            "Supposing dipendente will save same contributions"
                            "as he does for fondo pensione,"
                            "no yearly revalutation."
                    },
                    'isc': "Indice Sintetico di Costo, float"
                },
                'rendita':
                {
                    'durataAnni':
                        "How long (years) TFR wil last if same"
                        "retirement wage of that resulting from fondo pensione"
                        "is taken year-over-year,"
                        "float"

                }
            }
        }

    This is a class internally used by :py:class:`.ReportsDescIo`.
    """

    def __init__(self, reportId):
        """Constructor.

        :param int reportId: id of a report entry in DB.
        """
        common.DescIo.__init__(
            self, 'repResults', tableDef, tableTranslation)

        #: Id of the report to which dipendente's row is associated.
        self._reportId = reportId

    def _initDb(self):
        """DB initialization."""
        try:
            common.DescIo._conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS {}
                (descId INTEGER PRIMARY KEY,
                reportId INTEGER NOT NULL
                    REFERENCES reports(descId) ON DELETE CASCADE,
                {})'''.format(self._module, self._tableDef))
            common.DescIo._conn.execute('''
                CREATE INDEX IF NOT EXISTS {}Index ON {} (reportId)
                '''.format(self._module, self._module))
            common.DescIo._conn.commit()
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)

    def load(self):
        """Results' descriptor loading from db.

        This method is redefined here because:

        * No id is to be provided, since only one results record
          is associated to a report (id's stores in :py:data:`_reportId`).
        * Only the results record associated to a report has to be
          retrieved.

        """
        desc = []

        try:
            for row in common.DescIo._conn.execute(
                    'SELECT * FROM {} WHERE reportId=?'.format(
                        self._module),
                    (self._reportId,)):
                desc.append({})
                for k in row.keys():
                    try:
                        desc[-1][self._tableDescTranslation[k]] = row[k]
                    except KeyError:
                        desc[-1][k] = row[k]
        except sqlite3.Error as e:
            raise common.DataLoadStoreDbError(e)

        # Note: no deserialization is done. Left to the calling procedure
        return desc

    def save(self, desc, serialized=False):
        """Results' descriptor saving into db.

        This method is redefined here because the report's id has to be added
        to desc before trying saving it to DB. Saving is done by actually
        calling :py:meth:`.DescIo.save`.

        Refer to :py:meth:`.DescIo.save` for parameters and
        return value description.
        """
        tmpDesc = dict(desc)
        tmpDesc['reportId'] = self._reportId
        common.DescIo.save(self, tmpDesc, serialized)
