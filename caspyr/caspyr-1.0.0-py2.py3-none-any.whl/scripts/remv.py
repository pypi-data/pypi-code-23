#!/usr/bin/env python
"""REgexMove v%s
Usage:
  remv [options] <ipattern> <opattern>

Options:
  -n, --dry_run  : only print commands
  --log=<lvl>        Log level CRITICAL|ERROR|WARN(ING)|[default: INFO]|DEBUG.
%s
"""
from docopt import docopt
from argopt import DictAttrWrap
import logging
import re
from os import walk as os_walk
from shutil import move as shutil_move
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__all__ = ["main"]
__version__ = "0.1.1"


def main():
  args = DictAttrWrap(docopt(__doc__ % (__version__, __author__),
                             version=__version__))
  logging.basicConfig(level=getattr(logging, args.log, logging.NOTSET))
  log = logging.getLogger(__name__)
  allFiles = os_walk('.').next()[2]
  log.debug(args.ipattern)
  RE_IPAT = re.compile(args.ipattern)
  for f in allFiles:
    if RE_IPAT.search(f):
      dst = RE_IPAT.sub(args.opattern, f)
      log.info(' '.join(("mv", f, dst)))
      if not args.dry_run:
        shutil_move(f, dst)


if __name__ == "__main__":
  main()
