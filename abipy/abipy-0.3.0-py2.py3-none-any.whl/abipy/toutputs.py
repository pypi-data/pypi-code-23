#!/usr/bin/env python
from __future__ import print_function, division, unicode_literals, absolute_import

from abipy.abio.outputs import validate_output_parser

import sys

retcode = validate_output_parser(abitests_dir=sys.argv[1], output_files=None)
print(retcode)
