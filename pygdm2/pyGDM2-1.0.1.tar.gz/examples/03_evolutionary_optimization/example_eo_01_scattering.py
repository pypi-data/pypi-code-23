# encoding: utf-8
"""
Created on June 1, 2017

@author: P. R. Wiecha

"""

from pyGDM2 import core
from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2.EO.core import run_eo
from pyGDM2.EO.problems import ProblemScat
from pyGDM2.EO.models import RectangularAntenna



#==============================================================================
# Setup pyGDM part
#==============================================================================
## ---------- Setup structure
mesh = 'cube'
step = 15
material = materials.gold()   # structure material
n1, n2 = 1.0, 1.0             # vacuum environment

## --- Empty dummy-geometry, will be replaced on run-time by EO trial geometries
geometry = []       
struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))


## ---------- Setup incident field
field_generator = fields.planewave        # planwave excitation
kwargs = dict(theta = [0.0])              # target lin. polarization angle
wavelengths = [1000]                      # target wavelength
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## ---------- Simulation initialization
sim = core.simulation(struct, efield)


#==============================================================================
# setup evolutionary optimization
#==============================================================================
## --- structure model: Rectangular planar antenna of fixed height
limits_W   = [2, 20]  # units of "step"
limits_L   = [2, 20]  # units of "step"
limits_pos = []   # units of nm, [] -->  no shift allowed
height = 3    # units of "step"
model = RectangularAntenna(sim, limits_W, limits_L, limits_pos, height)

## --- optimization problem: Scattering
opt_target = 'Qscat'  # 'Qscat' --> scat. efficiency
problem = ProblemScat(model, opt_target=opt_target)


## --- filename to save results 
results_filename = 'eo_Qscat.eo'

## --- size of population
population = 15          # Nr of individuals

## --- stop criteria
max_time = 60            # seconds
max_iter = 20            # max. iterations
max_nonsuccess = 5      # max. consecutive iterations without improvement

## --- other config
generations = 1          # generations to evolve between status reports
plot_interval = 5        # plot each N improvements
save_all_generations = False

##  Use algorithm "sade" (jDE variant, a self-adaptive form of differential evolution)
import pygmo as pg
algorithm = pg.sade
algorithm_kwargs = dict()   # optional kwargs passed to the algorithm


eo_dict = run_eo(problem,
                 population=population,
                 algorithm=algorithm,
                 plot_interval=plot_interval, 
                 generations=generations, 
                 max_time=max_time, max_iter=max_iter, max_nonsuccess=max_nonsuccess,
                 filename=results_filename)


    