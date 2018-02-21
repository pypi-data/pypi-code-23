
# coding: utf-8

# This notebook is part of the $\omega radlib$ documentation: http://wradlib.org/wradlib-docs.
# 
# Copyright (c) 2016, $\omega radlib$ developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

# # RADOLAN 

# RADOLAN is abbreviated from the german **RA**dar-**O**n**L**ine-**AN**eichung, which means Radar-Online-Adjustment.
# 
# Using it's [network of 17 weather radar](https://www.dwd.de/SharedDocs/broschueren/DE/presse/Wetterradar_PDF.pdf?__blob=publicationFile&v=5>) the German Weather Service provides many products for high resolution precipitation analysis and forecast. A comprehensive product list can be found in chapter [RADOLAN Product Showcase](radolan/radolan_showcase.ipynb).
# 
# These composite products are distributed in the [RADOLAN Binary Data Format](radolan/radolan_format.ipynb) with an ASCII header. All composites are available in [Polar Stereographic Projection](radolan/radolan_grid.ipynb#Polar-Stereographic-Projection) which will be discussed in the chapter [RADOLAN Grid](radolan/radolan_grid.ipynb).

# - [RADOLAN Quick Start](radolan/radolan_quickstart.ipynb)
# - [RADOLAN Binary Data Format](radolan/radolan_format.ipynb)
# - [RADOLAN Product Showcase](radolan/radolan_showcase.ipynb)
# - [RADOLAN Grid](radolan/radolan_grid.ipynb)
# - [DWD Radar Network](radolan/radolan_network.ipynb)

# This notebook tutorial was prepared with material from the [DWD RADOLAN/RADVOR-OP Kompositformat](http://www.dwd.de/DE/leistungen/radolan/radolan_info/radolan_radvor_op_komposit_format_pdf.pdf?__blob=publicationFile&v=5>).
# We also wish to thank Elmar Weigl, German Weather Service, for providing the extensive set of example data and his valuable information about the RADOLAN products.
