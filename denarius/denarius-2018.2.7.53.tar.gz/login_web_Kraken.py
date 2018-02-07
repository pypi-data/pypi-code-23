#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# login_web_Kraken                                                             #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program logs into the Kraken website using Selenium.                    #
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
"""

import docopt
import os
import time
import sys

import che_guevara_otp
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

name    = "login_web_Kraken"
version = "2018-01-30T2238Z"

def main(options):

    filepath_credentials = os.path.expanduser("~/.kraken_credentials")
    if not os.path.isfile(filepath_credentials):
        print("no credentials file {filepath} found".format(filepath = filepath_credentials))
        sys.exit()
    with open(filepath_credentials, "r") as file_credentials:
        credentials_string = file_credentials.read()
    credentials = {}
    exec(credentials_string, credentials)
    username = credentials["username"]
    passcode = credentials["passcode"]
    secret   = credentials["secret"]

    driver = webdriver.Firefox()
    driver.get("https://www.kraken.com/en-us/login")
    time.sleep(2)
    element = driver.find_element_by_name("username")
    element.send_keys(username)
    element = driver.find_element_by_name("password")
    element.send_keys(passcode)
    element = driver.find_element_by_name("otp")
    element.send_keys(che_guevara_otp.TOTP(secret = secret))
    element.send_keys(Keys.RETURN)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
