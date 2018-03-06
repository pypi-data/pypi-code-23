from subprocess import Popen, PIPE

__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.0.0"


def sh(*cmd, **kwargs):
  return Popen(cmd, stdout=PIPE,
               **kwargs).communicate()[0].decode("utf-8")
