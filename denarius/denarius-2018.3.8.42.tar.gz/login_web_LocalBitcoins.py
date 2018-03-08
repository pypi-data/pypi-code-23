#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# login_web_LocalBitcoins                                                      #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program logs into the LocalBitcoins website using Selenium.             #
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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

name    = "login_web_LocalBitcoins"
version = "2018-01-31T1732Z"

def main(options):

    filepath_credentials = os.path.expanduser("~/.lbc")
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
    driver.get("https://localbitcoins.com/accounts/login/")
    time.sleep(2)
    # username
    element = driver.find_element_by_name("username")
    element.send_keys(username)
    # passcode
    element = driver.find_element_by_name("password")
    element.send_keys(passcode)
    time.sleep(1)
    # reCAPTCHA
    wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element_by_xpath('//iframe[contains(@src, "google.com/recaptcha")]')))
    wait(driver, 10).until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))).click()
    time.sleep(2)
    # login button
    driver.switch_to.default_content()
    elements = driver.find_elements_by_xpath("//button[contains(text(), 'Login')]")
    elements[0].click()
    # OTP   
    element = driver.find_element_by_name("token")
    element.send_keys(che_guevara_otp.TOTP(secret = secret))
    element.send_keys(Keys.RETURN)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
