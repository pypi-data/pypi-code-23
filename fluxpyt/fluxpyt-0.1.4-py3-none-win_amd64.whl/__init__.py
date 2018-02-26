# -*- coding: utf-8 -*-
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = '0.1.1'

from fluxpyt.main import main
from fluxpyt.monte_carlo import monte_carlo
from fluxpyt.bootstrap import bootstrap
from fluxpyt.draw_flux_map import draw_flux_map
