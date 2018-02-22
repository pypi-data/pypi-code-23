#!/usr/bin/env python
from abipy import abilab

ncfile = abilab.abiopen("al_888k_161616q_EPH.nc")

print(ncfile)
#ncfile.plot(what="lambda")
#ncfile.phbands_qpath.plot()
#ncfile.plot_eph_strength()
#ncfile.plot_with_a2f()

ncfile.a2f_qintp.plot_a2("_runflow/w2/t2/outdata/out_PHDOS.nc")