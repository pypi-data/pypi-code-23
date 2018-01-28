# -*- coding: utf-8 -*-


class UnsupportedDRMAAVersion(Exception):
    def __init__(self, ver):
        self.ver = ver

    def __str__(self):
        return "We only support DRMAA version 1.x - You have {}".format(self.ver)


class UnrecognizedQueueSystem(Exception):
    def __init__(self, contact, info, impl, version):
        self.args = (contact, info, impl, version)

    def __str__(self):
        return """Failed to recognize the current system.

Please report to the author(s) of jug_schedule and include the following

Contact : {0}
DRM Info: {1}
DRMAA   : {2}
Version : {3}
""".format(*self.args)


class CleanExit(Exception):
    "Raised when a fatal error ocurred but we should try to exit cleanly"


class UnsupportedFeature(Exception):
    "Raised when some behavior is not supported"


class MissingQueueIdentification(Exception):
    """Raised when drmaa is not available and it's not possible to identify the
    underlying system"""

    def __str__(self):
        return """Failed to recognize the current queue system.

If you are seeing this error after calling jug_schedule.identify_system() please
make sure drmaa is installed and configured correctly.

Alternatively run jug_schedule.identify_system(save=True) once from the master
node of the cluster. Note this only works if your home folder is shared across
nodes and is not shared between different clusters with different queue systems.
"""


# vim: ai sts=4 et sw=4
