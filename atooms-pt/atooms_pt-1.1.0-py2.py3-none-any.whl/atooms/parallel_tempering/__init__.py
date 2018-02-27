"""Parallel tempering simulation."""

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Daniele Coslovich <daniele.coslovich@umontpellier.fr>"

from .core import ParallelTempering
