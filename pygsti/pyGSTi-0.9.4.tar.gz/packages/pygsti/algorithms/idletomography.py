""" Idle Tomography algorithms """
from __future__ import division, print_function, absolute_import, unicode_literals
#*****************************************************************
#    pyGSTi 0.9:  Copyright 2015 Sandia Corporation
#    This Software is released under the GPL license detailed
#    in the file "license.txt" in the top-level pyGSTi directory
#*****************************************************************


import numpy          as _np
import scipy.optimize as _spo
import scipy.stats    as _stats
import warnings       as _warnings
import time           as _time

from .. import optimize     as _opt
from .. import tools        as _tools
from .. import objects      as _objs
from .. import baseobjs     as _baseobjs
from .. import construction as _pc


#Scratch:
#  We want d/d(eps) [ <meas| I+eps*error |prep> ] = <meas|error|prep>
#
# Hamiltonian case: error = i[err, rho], where err, prep and meas can be written as paulis,
#   so just group algebra.
#
# Need to convert prep/meas paulis -> gate sequences (what prepares an "X" density matrix)



#TODO:

def make_idletomography_list(...):
    pass

def do_idletomography(idleGateOrSyntheticIdle, basis, maxWeight, qubitGraph=None, ...):
    pass

