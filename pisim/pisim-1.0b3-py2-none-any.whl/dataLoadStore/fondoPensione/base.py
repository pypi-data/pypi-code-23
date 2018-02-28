# -*- coding: utf-8 -*-

"""I/O class for **fondo pensione, base** info.

Module's content
================

"""

from .. import common

#: Table definition. See :py:class:`~.common.DescIo` for further details.
tableDef = '''
    name TEXT {},
    tipo TEXT NOT NULL,
    accDipMinPerDatore REAL NOT NULL,
    accdDipBaseSottoMin TEXT NOT NULL,
    accdDipBaseSopraMin TEXT NOT NULL,
    accDatBase TEXT NOT NULL,
    accDatValore REAL NOT NULL
'''

#: Table-to-descriptor translation.
#: See :py:class:`~.common.DescIo` for further details.
tableTranslation = {
    'tipo': 'tipo',
    'accDipMinPerDatore':
        'accumulo.contribuzione.dipendente.minimaPerContributoDatore',
    'accdDipBaseSottoMin':
        'accumulo.contribuzione.dipendente.base.sottoMinima',
    'accdDipBaseSopraMin':
        'accumulo.contribuzione.dipendente.base.sopraMinima',
    'accDatBase': 'accumulo.contribuzione.datore.base',
    'accDatValore': 'accumulo.contribuzione.datore.valore'
}


class FpBaseDescIo(common.Model1DescIo):
    """I/O class for **fondo pensione, base** descriptors.

    Descriptor is a dictionary defined as follows::

        {
            'tipo': "fondo pensione type, in ['chiuso', 'aperto']",
            'accumulo':
            {
                # Common specs for fondo pensione, accumulo phase
                'contribuzione':
                {
                    # Common specs for dipendente
                    'dipendente':
                    {
                        'minimaPerContributoDatore':
                            "min amount of contribution from dipendente"+
                            "after which contribution from datore is due"+
                            "float",
                        # Salary base on which contribution from dipendente
                        # is computed
                        'base':
                        {
                            # All values here are from
                            # ['lordo', 'minContratto']
                            'sottoMinima':
                                "salary base for dipendente contribution"+
                                "below minimaPerContributoDatore",
                            'sopraMinima':
                                "salary base for dipendente contribution"+
                                "above minimaPerContributoDatore",
                        }
                    },
                    # Common specs for datore
                    'datore':
                    {
                        'base': "same as ['dipendente']['base']",
                        'valore': "contribution amount vs. 'base' from datore"
                    }
                }
            }
        }
    """

    def __init__(self):
        """Constructor."""
        common.Model1DescIo.__init__(
            self, 'fpBase', tableDef, tableTranslation)
