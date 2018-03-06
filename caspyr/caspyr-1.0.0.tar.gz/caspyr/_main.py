"""Usage:
  caspyr (--help|<script>) [options] [<args>...]

Options:
  -h, --help     : Print this help and exit.
  -v, --version  : Print module version number and exit.

Arguments:
  <script>  : %s
"""
from __future__ import print_function
import sys
from importlib import import_module
from glob import glob
from os.path import join, dirname, abspath
__all__ = ["main"]
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "1.0.0"


def main():
    positionals = filter(lambda a: not a.startswith('-'), sys.argv[1:])
    if not positionals:
        if any(h in sys.argv[1:] for h in ('-h', '--help')):
            pkgroot = abspath(dirname(__file__))
            scripts = [s.replace(join(pkgroot, "scripts", ""), "")[:-3]
                       for s in glob(join(pkgroot, "scripts", "*.py"))]
            scripts = [s for s in scripts if "__" not in (s[:2], s[-2:])]
            print(__doc__ % '|'.join(scripts), end="")
        elif any(v in sys.argv[1:] for v in ('-v', '--version')):
            from ._version import __version__ as modversion
            print(modversion + '-' + __version__)
        else:
            print(__doc__.split("\n\n", 1)[0])
    else:
        sys.argv = sys.argv[1:]
        script = import_module('.scripts.' + positionals[0], package='caspyr')
        script.main()


if __name__ == "__main__":
    main()
