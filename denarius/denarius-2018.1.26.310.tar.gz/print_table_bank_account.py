#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# print_table_bank_account                                                     #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program prints a table of the transactions of a bank account.           #
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
    -h, --help   display help message
    --version    display version and exit

    --bank=TEXT  bank to access  [default: Monzo]
"""

import docopt

import denarius.banks

name    = "print_table_bank_account"
version = "2018-01-21T0227Z"

def main(options):

    bank = options["--bank"]
    if bank == "Monzo":     denarius.banks.transactions_DataFrame_Monzo(print_table = True)
    if bank == "RBS":       denarius.banks.transactions_DataFrame_RBS(print_table = True)
    if bank == "Santander": denarius.banks.transactions_DataFrame_Santander(print_table = True)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
