#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# web_display_arbitrage_data                                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program loop displays Kraken LocalBitcoins UK arbitrage data on a web   #
# page.                                                                        #
#                                                                              #
# copyright (C) 2018 Will Breaden Madden, wbm@protonmail.ch                    #
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

import docopt
import os

import denarius
from flask import Flask, request
application = Flask(__name__)

name    = "web_display_arbitrage_data"
version = "2018-01-23T1808Z"
logo    = None

def main(options):

    global filepath_CSV
    global interval
    global volume_EUR

    filepath_CSV = os.path.expanduser(options["--CSV"])
    interval     = int(options["--interval"])
    volume_EUR   = float(options["--volume_EUR"])

    application.run(
        host = "0.0.0.0",
        port = 8081
    )

@application.route("/")
def form():
    return denarius.printout_arbitrage_Kraken_LocalBitcoins_UK(
        filepath_CSV = filepath_CSV,
        volume_EUR   = volume_EUR
    ).replace("\n", "<br/>")

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
