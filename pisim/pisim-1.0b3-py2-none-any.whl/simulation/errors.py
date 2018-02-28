# -*- coding: utf-8 -*-

"""Errors raised by :py:meth:`.FpSim.run`.

Module's content
================

"""


class SimulationBaseError(Exception):
    """Package base exception class, does nothing."""

    pass


class NotPositiveYearsError(SimulationBaseError):
    """Raised if the development plan years is non positive."""

    def __init__(self, years):
        """Constructor."""
        self.years = years

    def __str__(self):
        """Return the error string."""
        return "Anni di sviluppo piano non positivi ({})".format(self.years)


class TooManyYearsError(SimulationBaseError):
    """Raised if the plan development spans too many years."""

    def __init__(self, years, limit):
        """Constructor."""
        self.years = years
        self.limit = limit

    def __str__(self):
        """Return the error string."""
        return "Anni di sviluppo piano ({})eccedenti il limite ({})".format(
            self.years, self.limit)
