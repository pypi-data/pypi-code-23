#!/usr/bin/env python
from abipy import abilab
import abipy.data as abidata

def main_pmg():
    mpid = "mp-149"
    mpid = "mp-856"
    mpid = "mp-3079"

    #from pymatgen.matproj.rest import MPRester
    #rest = MPRester()
    #pmgb = rest.get_bandstructure_by_material_id(material_id=mpid)
    #structure = rest.get_structure_by_material_id(mpid, final=True)
    #if pmgb.structure is None:
    #    pmgb.structure = structure
    #pmgb = pmgb.__class__.from_dict(pmgb.as_dict())
    #from pprint import pprint
    #pprint(vars(pmgb))
    #for k in pmgb.kpoints:
    #    print(k)
    #from pymatgen.electronic_structure.plotter import BSPlotter
    #BSPlotter(pmgb).get_plot().show()

    ebands = abilab.ElectronBands.from_material_id(mpid)
    print(ebands.structure)

    #pmgb.get_vbm()
    #nelect = 8
    #same_ebands = abilab.ElectronBands.from_pymatgen(pmgb, nelect)
    #print(same_ebands)

    ebands = ebands.new_with_irred_kpoints(prune_step=2)
    #print(ebands)
    #print(ebands.kpoints)

    ebands.plot()
    r = ebands.interpolate(lpratio=50, kmesh=[10, 10, 10])

    edos = r.ebands_kmesh.get_edos()
    r.ebands_kpath.plot_with_edos(edos)


def main_abinit():
    #print(b)
    #print(b.structure)
    #data = rest.get_data(mpid, prop="bandstructure")
    #pprint(data)
    #return

    path = abidata.ref_file("si_nscf_GSR.nc")
    path = abidata.ref_file("si_scf_GSR.nc")

    path = abidata.ref_file("ni_666k_GSR.nc")
    path = abidata.ref_file("ni_kpath_GSR.nc")

    ebands = abilab.ElectronBands.from_file(path)
    ebands.plot()
    #nelect = ebands.nelect
    return
    nelect = 8

    pmg = ebands.to_pymatgen()
    print(pmg)

    #from pymatgen.electronic_structure.plotter import BSPlotter
    #BSPlotter(pmg).get_plot().show()

    same_ebands = abilab.ElectronBands.from_pymatgen(pmg, nelect)
    print("same_ebands\n", same_ebands)
    #same_ebands.plot()

    r = same_ebands.interpolate()
    r.ebands_kpath.plot()


def main_new():
    import pickle
    mpid = "mp-149"
    mpid = "mp-856"

    ebands = abilab.ElectronBands.from_material_id(mpid)
    #print(ebands)
    #return

    pickle_file = "ebands.pickle"
    #with open(pickle_file, "wb") as fh:
    #    pickle.dump(ebands, fh)
    #return

    #with open(pickle_file, "rb") as fh:
    #    ebands = pickle.load(fh)

    print(ebands.structure.reciprocal_lattice)
    print(ebands.kpoints.ksampling)
    #print(ebands.kpoints)
    #ebands.structure.show_bz()
    #ebands.plot()
    #return

    # Remove redundant k-points.
    # Use prune_step to remove additional k-points with [::prune_step]
    #ebands = ebands.new_with_irred_kpoints(prune_step=None)
    ebands = ebands.new_with_irred_kpoints(prune_step=2)
    #print(ebands); print(ebands.kpoints)
    #ebands.plot()

    # The default value is lpratio is 5 but more complicated bands could require a larger value.
    r = ebands.interpolate(lpratio=20)
    r.ebands_kpath.plot()

if __name__ == "__main__":
    #main_new()
    main_pmg()
    #main_abinit()
