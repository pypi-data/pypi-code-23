#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# loop_save_RBS_to_CSV                                                         #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program gets the recent transactions of an RBS account using Firefox    #
# and Selenium and saves them to CSV.                                          #
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
    -h, --help        display help message
    --version         display version and exit

    --CSV=FILEPATH    bank account CSV                       [default: ./RBS.csv]
    
    --interval=INT    time between recordings (s)            [default: 30]
    --sleep_time=INT  time between website interactions (s)  [default: 6]
"""

import docopt
import os

import denarius.RBS

name    = "loop_save_RBS_to_CSV"
version = "2018-01-21T0227Z"

def main(options):

    filepath_CSV = os.path.expanduser(options["--CSV"])
    interval     =                int(options["--interval"])
    sleep_time   =                int(options["--sleep_time"])

    denarius.RBS.loop_save_transactions_to_CSV(
        filepath_CSV = filepath_CSV,
        sleep_time   = sleep_time,
        interval     = interval
    )

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
