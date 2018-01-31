# -*- coding: utf-8 -*-
"""
This package contains object classes and functions to work with LAMMPS files within Python.

"""

__license__   = "MIT"
__docformat__ = 'reStructuredText'
__version__   = '0.1.3'



from ._block import (DataBlock, ThermoBlock, FixBlock)
from ._datafile import (SimpleDataFile, FixBlockFile, LogFile)
from ._lmpdatafile import (LammpsDataFile, LammpsDataHeader, LammpsDataMasses, LammpsDataCoeffs, LammpsDataAtoms,
                           LammpsDataVelocities, LammpsDataAtomTemplate, LammpsDataCoeffsSection, LammpsDataAtomAtomic)


__all__ = ( 'IndexedFile' , 'Block', 'BlockFile',
           'SimpleDataFile', 'FixBlockFile', 'LogFile',
            'ThermoBlock','DataBlock', 'FixBlock',
            'LammpsDataFile', 'LammpsDataHeader', 'LammpsDataMasses', 'LammpsDataCoeffs', 'LammpsDataAtoms',
            'LammpsDataVelocities', 'LammpsDataAtomTemplate', 'LammpsDataCoeffsSection', 'LammpsDataAtomAtomic')
