#!/usr/bin/env python

from abipy import abilab

import sys
#path = sys.argv[1]
path = "si_scf_WFK.nc"

ncfile = abilab.abiopen(path)

ncfile.classify_states(spin=0, kpoint=0)
