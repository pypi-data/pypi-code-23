#!/usr/bin/env python

from abipy import abilab

import sys
path = sys.argv[1]

ncfile = abilab.abiopen(path)

#den = ncfile.density
##den.integrate_in_spheres(rcut_symbol=dict(Si=2, Ni=2))
#den.integrate_in_spheres(rcut_symbol=None)
#print("magnetization:", den.magnetization)

print(ncfile.ebands.kpoints)
ncfile.ebands.plot_transitions(float(sys.argv[2]), atol_ev=float(sys.argv[3]))
#ncfile.ebands.plot_transitions(float(sys.argv[2]), qpt=[-0.08333, 0, 0], atol_ev=float(sys.argv[3]), atol_diff=12.8)
#ncfile.ebands.plot_transitions(float(sys.argv[2]), qpt=[+0.03, 0, 0], atol_ev=float(sys.argv[3]), atol_kdiff=0.2)