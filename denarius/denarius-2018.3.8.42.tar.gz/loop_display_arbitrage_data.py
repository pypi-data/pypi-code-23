#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# loop_display_arbitrage_data                                                  #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program loop displays Kraken LocalBitcoins UK arbitrage data.           #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help          display help message
    --version           display version and exit

    --CSV=FILEPATH      filepath of CSV data          [default: arbitrage_Kraken_LocalBitcoins_UK.csv]

    --interval=INT      time between recordings (s)   [default: 60]

    --volume_EUR=FLOAT  EUR volume used in arbitrage  [default: 9000]
"""

from __future__ import division
import docopt
import os
import sys
import textwrap
import time

import denarius
import pandas as pd

name    = "loop_display_arbitrage_data"
version = "2018-01-23T1746Z"
logo    = None

def main(options):

    filepath_CSV = os.path.expanduser(options["--CSV"])
    interval     = int(options["--interval"])
    volume_EUR   = float(options["--volume_EUR"])

    while True:
        print(denarius.printout_arbitrage_Kraken_LocalBitcoins_UK(
            filepath_CSV = filepath_CSV,
            volume_EUR   = volume_EUR
        ))
        time.sleep(interval)
        os.system("clear")

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
