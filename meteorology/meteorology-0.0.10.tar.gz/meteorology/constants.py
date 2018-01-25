#!/usr/bin/env python3

# system modules

# internal modules

# external modules


### Temperature ###
zero_celsius_in_kelvin = 273.15
r"""
Zero degrees Celsius in Kelvin

:math:`\left[T_\mathrm{0^\circ C}\right] = K`

https://de.wikipedia.org/wiki/Kelvin
"""

### Gas constants ###
gas_constant_univeral = 8.3144598
r"""
universal gas constant 

:math:`\left[R^*\right] = \frac{J}{mol\,K}`

https://de.wikipedia.org/wiki/Gaskonstante
"""

gas_constant_water_vapour = 461.4
r"""
specific gas constant of water vapour

:math:`\left[R_\mathrm{watervapour}\right] = \frac{J}{kg\,K}`

https://de.wikipedia.org/wiki/Gaskonstante
"""

gas_constant_dry_air = 287.058
r"""
specific gas constant of dry air

:math:`\left[R_\mathrm{dryair}\right] = \frac{J}{kg\,K}`

https://de.wikipedia.org/wiki/Gaskonstante
"""

gas_constant_co2 = 188.9
r"""
specific gas constant of carbon dioxide

:math:`\left[R_\mathrm{CO2}\right] = \frac{J}{kg\,K}`

https://de.wikipedia.org/wiki/Gaskonstante
"""

### radiation ###
stefan_boltzmann_constant = 5.670367e-8
r"""
Stefan-Boltzmann constant for blackbody-radiation

:math:`\left[\sigma\right] = \frac{W}{m^2\,K^4}`

https://de.wikipedia.org/wiki/Stefan-Boltzmann-Gesetz
"""

solar_constant_toa = 1367
r""" 
solar constant at top of atmosphere

:math:`\left[I_0\right] = \frac{W}{m^2}`

https://de.wikipedia.org/wiki/Solarkonstante
"""

### material ###
density_water_0C = 999.87
r"""
density of water at :math:`0^\circ C` and standard sea-level atmospheric
pressure

:math:`\left[\rho_\mathrm{water,0^\circ C}\right] = \frac{kg}{m^3}`

https://water.usgs.gov/edu/density.html
"""

density_water_4C = 1000.0
r"""
density of water at :math:`4^\circ C` and standard sea-level atmospheric
pressure

:math:`\left[\rho_\mathrm{water,4^\circ C}\right] = \frac{kg}{m^3}`

https://water.usgs.gov/edu/density.html
"""

### heat capacities ###
specific_heat_capacity_dry_air = 1005
r""" 
specific heat capacity of dry air at constant pressure

:math:`\left[c_\mathrm{p,dryair}\right] = \frac{J}{kg\,K}`

https://de.wikipedia.org/wiki/Spezifische_Wärmekapazität
"""

### vaporization enthalpies ###
enthalpy_of_vaporization_water_100C = 2257e3
r""" 
enthalpy of vapourization of liquid water

:math:`\left[L_\mathrm{water,100^\circ C}\right] = \frac{J}{kg}`

https://en.wikipedia.org/wiki/Enthalpy_of_vaporization
"""
