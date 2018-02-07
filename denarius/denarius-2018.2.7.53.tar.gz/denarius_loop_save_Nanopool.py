#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius_loop_save_Nanopool                                                  #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program loop records Nanopool data for an address.                      #
#                                                                              #
# copyright (C) 2018 Will Breaden Madden                                       #
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

    --addresses=TEXT  address or comma-separated addresses
    --CSV=FILENAME    filename for saving CSV data                     [default: Nanopool.csv]
    --interval=FLOAT  loop time interval (s)                           [default: 120]
    --print_table     print table of current data each recording loop
"""

import datetime
import docopt
import os
import requests
import sys
import time

import pandas as pd
import pyprel

name    = "denarius_loop_save_Nanopool"
version = "2018-02-03T1122Z"

def main(options):

    addresses    =                    options["--addresses"]
    filepath_CSV = os.path.expanduser(options["--CSV"])
    interval     =              float(options["--interval"])
    print_table  =                    options["--print_table"]
    if not addresses:
        print("error -- no address specified")
        sys.exit()
    addresses = addresses.split(",")
    while True:
        for address in addresses:
            try:
                response_user     = requests.get("https://api.nanopool.org/v1/eth/user/" + address).json()
                time.sleep(3)
                response_earnings = requests.get("https://api.nanopool.org/v1/eth/approximated_earnings/" + response_user["data"]["hashrate"]).json()
                time.sleep(3)
                hashrate_pool     = requests.get("https://api.nanopool.org/v1/eth/pool/hashrate").json()["data"]
                time.sleep(3)
                pool_miners       = requests.get("https://api.nanopool.org/v1/eth/pool/activeminers").json()["data"]
                time.sleep(3)
                pool_workers      = requests.get("https://api.nanopool.org/v1/eth/pool/activeworkers").json()["data"]
                df = pd.DataFrame(columns = ["datetime"])
                df = df.append(
                    {
                        "datetime"               : datetime.datetime.utcnow(),
                        "account"                : response_user["data"]["account"    ],
                        "balance"                : response_user["data"]["balance"    ],
                        "hashrate"               : response_user["data"]["hashrate"   ],
                        "hashrate1hr"            : response_user["data"]["avgHashrate"]["h1"],
                        "hashrate3hr"            : response_user["data"]["avgHashrate"]["h3"],
                        "hashrate6hr"            : response_user["data"]["avgHashrate"]["h6"],
                        "hashrate12hr"           : response_user["data"]["avgHashrate"]["h12"],
                        "hashrate24hr"           : response_user["data"]["avgHashrate"]["h24"],
                        "earnings_per_minute_ETH": response_earnings["data"]["minute"]["coins"   ],
                        "earnings_per_minute_BTC": response_earnings["data"]["minute"]["bitcoins"],
                        "earnings_per_minute_EUR": response_earnings["data"]["minute"]["euros"   ],
                        "earnings_per_hour_ETH"  : response_earnings["data"]["hour"  ]["coins"   ],
                        "earnings_per_hour_BTC"  : response_earnings["data"]["hour"  ]["bitcoins"],
                        "earnings_per_hour_EUR"  : response_earnings["data"]["hour"  ]["euros"   ],
                        "earnings_per_day_ETH"   : response_earnings["data"]["day"   ]["coins"   ],
                        "earnings_per_day_BTC"   : response_earnings["data"]["day"   ]["bitcoins"],
                        "earnings_per_day_EUR"   : response_earnings["data"]["day"   ]["euros"   ],
                        "earnings_per_week_ETH"  : response_earnings["data"]["week"  ]["coins"   ],
                        "earnings_per_week_BTC"  : response_earnings["data"]["week"  ]["bitcoins"],
                        "earnings_per_week_EUR"  : response_earnings["data"]["week"  ]["euros"   ],
                        "earnings_per_month_ETH" : response_earnings["data"]["month" ]["coins"   ],
                        "earnings_per_month_BTC" : response_earnings["data"]["month" ]["bitcoins"],
                        "earnings_per_month_EUR" : response_earnings["data"]["month" ]["euros"   ],
                        "hashrate_pool"          : hashrate_pool,
                        "pool_miners"            : pool_miners,
                        "pool_workers"           : pool_workers
                    },
                    ignore_index = True
                )
                df.to_csv(filepath_CSV, header = not os.path.isfile(filepath_CSV), index = False, mode = "a")
                if print_table:
                    print(pyprel.Table(contents = pyprel.table_DataFrame(df = df)))
            except:
                print("error")
                pass
            time.sleep(30)
        print("\nwait {interval} s".format(interval = interval))
        time.sleep(interval)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
