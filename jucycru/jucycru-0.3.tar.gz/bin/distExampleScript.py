#!/usr/bin/env python

"""
This example returns the altitude of JUICE above Earth during the time window
specified by start_time and end_time.

For this script to run on your computer you should ensure you have the following
packages installed:

    math | numpy | spiceypy | matplotlib | jucycru

And you must change the kpath string to the absolute path to the kernel folder
for the relevant mission (in this case JUICE).

This example uses the latest mk file (juice_crema_3_2_v160.tm). This can be changed
to older version by changing the crema string to the crema version i.e. 3_0 and the
crema_version to the version of the mk spice file i.e. v152.

The start_time and end_time can be any date in the form of the string as long as
there is sufficient ephemeris data for the spacecraft and bodies loaded within the
metakernel.

The main_body can be changed to other solar system bodies and will be used as the
central object for any plots the be produced.

The resolution is the step size in the time array; for smaller time windows it
is best to use a smaller resolution (for large time windows and small resolution
the computation time will be longer)

Other bodies can be included in the plot by including them in other_bodies variable
    i.e. other_bodies = 'Callisto', 'Europa', 'Ganymede'
and should follow the above format

If CA is included it will change the plot type to give time to closest approach
on the x axis (WARNING: CA is not calculated at any point so must be set correctly).
CA must be a date in a string format (see in script example for more information)

ADDITIONAL FUNCTIONALITIES STILL TO BE IMPLEMENTED:

Plot types for different variables [i.e. phase_angle]

"""

import jucycru as jc
import spiceypy as spice

# REQUIRED INPUTS
start_time = '2023 MAY 10 00:00:00'
end_time = '2023 JUN 10 00:00:00'
crema = '3_2'
crema_version = 'v160'
main_body = 'Earth'

# CHANGE THIS TO PATH/TO/KERNELS FOLDER
kpath = '/Applications/cosmographia/Missions/spicekernels/JUICE/'

# RECOMMENDED INPUT
res = 3600

# DEFAULT INPUTS
other_bodies = []
CA = 0
spacecraft = 'JUICE'

# ALTERNATIVE DEFAULT INPUT FORMAT EXAMPLES
# other_bodies = 'Phobos', 'Deimos'
# CA = '2025 FEB 10 18:00:00'

# PLOT TYPE - NOT FUNCTIONAL YET
# ptype = 'distlog'

# CONFIGURE KERNEL POOL
mkpath = 'mk/juice_crema_'
kfurnsh = kpath + mkpath + crema + '_' + crema_version + '.tm'
spice.furnsh(kfurnsh)

# FORMAT AND CREATE TIME VARIABLES/ARRAYS
[et1, et2, nintvl, times] = jc.tconst(start_time, end_time, resolution=res)

# CALCULATE GEOMETRY AND ILLUMINATION PARAMETERS
[phase_angle, distance, angular_diameter,
 solar_elongation, body_separation,
 main_body_radius] = jc.geometry(et1, et2, main_body, spacecraft,
                                 other_bodies=other_bodies, resolution=res)

# PLOT DESIRED PARAMETER
jc.plot(times, distance, main_body, main_body_radius,
        other_bodies=other_bodies, resolution=res, Closest_Approach=CA)
