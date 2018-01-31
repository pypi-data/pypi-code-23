#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# buy_BTC_for_EUR_last_price_on_Kraken                                         #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program buys Bitcoin for the last market price in Euros on Kraken.      #
#                                                                              #
# copyright (C) 2018 William Breaden Madden                                    #
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
    --volume=FLOAT  volume in BTC [default: 0.002]
"""

import docopt
import sys

import denarius.Kraken

name    = "buy_BTC_for_EUR_last_price_on_Kraken"
version = "2018-01-31T0010Z"

def main(options):

    volume_in_BTC = float(options["--volume"])
    denarius.Kraken.start_API()
    print(denarius.Kraken.buy_XBT_for_EUR(volume_in_BTC = volume_in_BTC))

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    main(options)
