#!/usr/bin/env python

"""Utility to write the headers of all frames of a FITS file into a text file output.

Output filename will be "<name-of-fits-file>.txt".
"""

import sys
import ariastro


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print(__doc__)
        print("")
        print("Usage: dump-header.py <name-of-fits-file>")
        print("")
        sys.exit()

    ariastro.dump_header(sys.argv[1])