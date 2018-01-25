#!/usr/bin/env python

# Copyright (C) Duncan Macleod (2014)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.

"""Calculating (and plotting) rate versus time for an `EventTable`

I would like to study the rate at which event triggers are generated by the
`ExcessPower` gravitational-wave burst detection algorithm, over a small
stretch of data.

The data from which these events were generated are a simulation of Gaussian noise
with the Advanced LIGO design spectrum, and so don't actually contain any real
gravitational waves, but will help tune the algorithm to improve detection of
future, real signals.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__currentmodule__ = 'gwpy.table'

# First, we import the `EventTable` object and read in a set of events from
# a LIGO_LW-format XML file containing a
# :class:`sngl_burst <glue.ligolw.lsctables.SnglBurstTable>` table
from gwpy.table import EventTable
events = EventTable.read('H1-LDAS_STRAIN-968654552-10.xml.gz',
                         tablename='sngl_burst', columns=['time', 'snr'])

# .. note::
#
#    Here we manually specify the `columns` to read in order to optimise
#    the `read()` operation to parse only the data we actually need.

# We can calculate the rate of events (in Hertz) using the
# :meth:`~EventTable.event_rate` method:
rate = events.event_rate(1, start=968654552, end=968654562)

# The :meth:`~EventTable.event_rate` method has returned a
# `~gwpy.timeseries.TimeSeries`, so we can display this using the
# :meth:`~gwpy.timeseries.TimeSeries.plot` method of that object:
plot = rate.plot()
plot.set_xlim(968654552, 968654562)
plot.set_ylabel('Event rate [Hz]')
plot.set_title('LIGO Hanford Observatory event rate for GW100916')
plot.show()
