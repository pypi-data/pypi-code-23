#!/usr/bin/env python
from abipy import abilab
from abipy.electrons.scissors import ScissorsBuilder

import abipy.data as abidata

builder = ScissorsBuilder.from_file(abidata.ref_file("si_g0w0ppm_nband30_SIGRES.nc"))
assert builder.nsppol == 1
#builder.pickle_dump()
#ScissorsBuilder.pickle_load()

# To plot the QP results as function of the KS energy:
builder.plot_qpe_vs_e0()

# To select the domains esplicitly (optional)
builder.build(domains_spin=[[-10, 6.02], [6.1, 20]])

# To compare the fitted results with the ab-initio data:
builder.plot_fit()

# To plot the corrected bands:
bands_filepath = abidata.ref_file("si_nscf_WFK.nc")
builder.plot_qpbands(bands_filepath)

dos_filepath = abidata.ref_file("si_scf_GSR.nc")
builder.plot_qpbands(bands_filepath, dos_filepath=dos_filepath, dos_args=None)
