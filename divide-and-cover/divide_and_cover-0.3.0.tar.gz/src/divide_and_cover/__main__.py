#!/usr/bin/env python3

import sys

from . import coverage_handler


coverage_handler.UNDER_WRAPPER = True
coverage_handler.coverage_script.command_line(sys.argv[1:])
