import pathlib
import sys

from .make2help import parse_makefile, prepare_makefile_lines, format_makehelp


def main():
    """Search Makefile at current directory and show help."""
    makefile = pathlib.Path('./Makefile')
    if not makefile.is_file():
        print('There is no Makefile at {}'.format(
            pathlib.Path('.').absolute()))
        sys.exit(1)
    lines = prepare_makefile_lines(makefile)
    for target, detail in parse_makefile(lines):
        print(format_makehelp(target, detail))
