"""
.. module:: orgasm.assembler
   :platform: Unix
   :synopsis: The :py:mod:`orgasm.assembler` python package provide the :class:`Assembler` class .

The :py:mod:`orgasm.assembler` package
======================================

:author:  Eric Coissac
:contact: eric.coissac@inria.fr

The :py:mod:`orgasm.assembler` python package provide the :class:`Assembler` class 
which manage the assembling process.
"""

from ._assembler import Assembler       # @UnresolvedImport
from ._assembler import buildstem       # @UnresolvedImport
from ._tango import tango,getusedreads,resetusedreads  # @UnresolvedImport
