"""Entry point for easy dump of PCF configuration lines.

This module can be run as a standalone and will dump the PCF files needed to add to
COMPSs executions in order to include dataClay events in its trace.
"""

from . import pcf_dataclay_addendum


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    pcf_dataclay_addendum()  # this will log the expected lines, correctly formatted
