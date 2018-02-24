"""
Documentation for ``empyscripts``, the add-ons for ``empymod``.

The add-ons are all independent of each other, and have their own
documentation. You can find the information of each add-on in the respective
*Code*-section.

For more information regarding installation, usage, add-ons, contributing,
roadmap, bug reports, and much more, see https://empymod.github.io.


License
-------

Copyright 2017-2018 Dieter Werthmüller

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

.. |_| unicode:: 0xA0
   :trim:


References |_|
--------------

.. [Anderson_1975] Anderson, W. L.,  1975, Improved digital filters for
   evaluating Fourier and Hankel transform integrals: USGS, PB242800;
   `pubs.er.usgs.gov/publication/70045426
   <https://pubs.er.usgs.gov/publication/70045426>`_.
.. [Chave_and_Cox_1982] Chave, A. D., and C. S. Cox, 1982, Controlled
   electromagnetic sources for measuring electrical conductivity beneath the
   oceans: 1. forward problem and model study: Journal of Geophysical Research,
   87, 5327-5338; DOI: |_| `10.1029/JB087iB07p05327
   <http://doi.org/10.1029/JB087iB07p05327>`_.
.. [Ghosh_1970] Ghosh, D. P.,  1970, The application of linear filter theory to
   the direct interpretation of geoelectrical resistivity measurements: Ph.D.
   Thesis, TU Delft; UUID: |_| `88a568bb-ebee-4d7b-92df-6639b42da2b2
   <http://resolver.tudelft.nl/uuid:88a568bb-ebee-4d7b-92df-6639b42da2b2>`_.
.. [Guptasarma_and_Singh_1997] Guptasarma, D., and B. Singh, 1997, New digital
   linear filters for Hankel J0 and J1 transforms: Geophysical Prospecting, 45,
   745--762; DOI: |_| `10.1046/j.1365-2478.1997.500292.x
   <http://dx.doi.org/10.1046/j.1365-2478.1997.500292.x>`_.
.. [Hunziker_et_al_2015] Hunziker, J., J. Thorbecke, and E. Slob, 2015, The
   electromagnetic response in a layered vertical transverse isotropic medium:
   A new look at an old problem: Geophysics, 80(1), F1--F18;
   DOI: |_| `10.1190/geo2013-0411.1
   <http://doi.org/10.1190/geo2013-0411.1>`_;
   Software: `software.seg.org/2015/0001 <http://software.seg.org/2015/0001>`_.
.. [Key_2009] Key, K., 2009, 1D inversion of multicomponent, multifrequency
   marine CSEM data: Methodology and synthetic studies for resolving thin
   resistive layers: Geophysics, 74(2), F9--F20; DOI: |_| `10.1190/1.3058434
   <http://doi.org/10.1190/1.3058434>`_.
   Software: `marineemlab.ucsd.edu/Projects/Occam/1DCSEM
   <http://marineemlab.ucsd.edu/Projects/Occam/1DCSEM>`_.
.. [Key_2012] Key, K., 2012, Is the fast Hankel transform faster than
   quadrature?: Geophysics, 77, F21--F30; DOI: |_| `10.1190/GEO2011-0237.1
   <http://dx.doi.org/10.1190/GEO2011-0237.1>`_;
   Software: `software.seg.org/2012/0003 <http://software.seg.org/2012/0003>`_.
.. [Kong_2007] Kong, F. N., 2007, Hankel transform filters for dipole antenna
   radiation in a conductive medium: Geophysical Prospecting, 55, 83--89;
   DOI: |_| `10.1111/j.1365-2478.2006.00585.x
   <http://dx.doi.org/10.1111/j.1365-2478.2006.00585.x>`_.
.. [Werthmuller_2017] Werthmüller, D., 2017, An open-source full {3D}
   electromagnetic modeler for 1D VTI media in Python: empymod: Geophysics, 82,
   WB9--WB19.; DOI: |_| `10.1190/geo2016-0626.1
   <http://doi.org/10.1190/geo2016-0626.1>`_.
.. [Ziolkowski_and_Slob_2018] Ziolkowski, A., and E. Slob, 2018, Introduction
   to Controlled-Source Electromagnetic Methods: Cambridge University Press;
   expected to be published late 2018.

"""
# Copyright 2017-2018 Dieter Werthmüller
#
# This file is part of empyscripts.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

from . import tmtemod
from . import fdesign
from .printinfo import versions

__all__ = ['tmtemod', 'fdesign', 'versions']

# Version
__version__ = '0.3.1'
