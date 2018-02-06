# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# RBS                                                                          #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides banking and other utilities.                           #
#                                                                              #
# copyright (C) 2017 William Breaden Madden                                    #
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
"""

import decimal
import docopt
import os
import re
import sys
import time

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

name    = "RBS"
version = "2018-01-18T1452Z"

def account_status(
    filepath_credentials               = "~/.rbs",
    convert_currency_strings_to_floats = True,
    log_out                            = True,
    close_driver                       = True,
    sleep_time                         = 6
    ):

    """
    Access RBS online banking using credentials specified or from a file. Get
    the balance and transactions for the account specified. Return a dictionary
    of the balance and a DataFrame of recent transactions. Return None if there
    is an error.

    The form of the DataFrame of recent transactions is something like the
    following:

         date                                   description  amount
    0  13 Jan                             CALL REF.NO. 1234  -500.0
    1  05 Jan    L. RON HUBBARD\nDigital/Mobile Transaction  -950.0
    2  04 Jan      J. H. CHRIST\nDigital/Mobile Transaction    -5.0
    3  02 Jan                   M. F. GOD\nAutomated Pay In   100.0
    4  02 Jan                     GANESHA\nAutomated Pay In   250.0
    5  02 Jan                  G. V. FUNK\nAutomated Pay In   950.0
    6  02 Jan                    DR. ZEUS\nAutomated Pay In   100.0
    7  28 Dec                       DAGDA\nAutomated Pay In    90.0
    8  27 Dec                     WEI DAI\nAutomated Pay In    20.0
    9  27 Dec            C. COLLINS-TOOTH\nAutomated Pay In   500.0

    The date is not specified in the web interface with time, so this field is
    not converted to a datetime.
    """

    # access credentials from file
    filepath_credentials = os.path.expanduser(filepath_credentials)
    if not os.path.isfile(filepath_credentials):
        print("no credentials file {filepath} found".format(filepath = filepath_credentials))
        sys.exit()
    with open(filepath_credentials, "r") as file_credentials:
        credentials_string = file_credentials.read()
    credentials = {}
    exec(credentials_string, credentials)
    customer_number = credentials["customer_number"]
    PIN             = credentials["PIN"]
    passcode        = credentials["passcode"]
    account_code    = credentials["account_code"]
    try:
        driver = webdriver.Firefox()
        driver.get("http://personal.rbs.co.uk")
        # login button
        button_login = driver.find_element_by_class_name("gnav-login-button")
        button_login.click()
        time.sleep(sleep_time)
        # enter customer number
        driver.switch_to_frame("ctl00_secframe")
        element = driver.find_element_by_name("ctl00$mainContent$LI5TABA$CustomerNumber_edit")
        element.click()
        element.send_keys(customer_number)
        element.send_keys(Keys.RETURN)
        time.sleep(sleep_time)
        # enter PIN
        for box in ["A", "B", "C"]:
            element = driver.find_element_by_name("ctl00$mainContent$Tab1$LI6PPE" + box + "_edit")
            element.click()
            element.send_keys(PIN[find_ordinal(driver.find_element_by_id("ctl00_mainContent_Tab1_LI6DDAL" + box + "Label").text) - 1])
        # enter passcode
        for box in ["D", "E", "F"]:
            element = driver.find_element_by_name("ctl00$mainContent$Tab1$LI6PPE" + box + "_edit")
            element.click()
            element.send_keys(passcode[find_ordinal(driver.find_element_by_id("ctl00_mainContent_Tab1_LI6DDAL" + box + "Label").text) - 1])
        # next button
        element = driver.find_element_by_name("ctl00$mainContent$Tab1$next_text_button_button")
        element.click()
        time.sleep(sleep_time)
        # get statement element and balance
        statement = driver.find_element_by_id("Account_" + account_code)
        balance   = statement.text.split()[-2] # string with pounds symbol
        # get transactions table
        statement.click()
        time.sleep(1)
        transactions = driver.find_element_by_class_name("tranTable")
        # convert transactions table to DataFrame
        df = pd.DataFrame(columns = ["date"])
        for row in transactions.find_elements_by_tag_name("tr"):
            columns = row.find_elements_by_tag_name("td")
            columns = [column.text.rstrip("-") for column in columns]
            if columns:
                df = df.append(
                    {
                        "date":        columns[0],
                        "description": columns[1],
                        "amount":      columns[2]
                    },
                    ignore_index = True
                )
        df = df[["date", "description", "amount"]]
        if log_out:
            driver.get("https://www.rbsdigital.com/ServiceManagement/RedirectOutOfService.aspx?targettag=destination_ExitService&amp;secstatus=0")
        if close_driver:
            driver.quit()
        if convert_currency_strings_to_floats:
            balance      = currency_string_to_float(balance)
            df["amount"] = df.apply(lambda x: currency_string_to_float(x["amount"]), axis = 1)
        return {
            "balance":      balance,
            "transactions": df
        }
    except:
        try:
            driver.quit()
        except:
            pass
        return None

def loop_save_transactions_to_CSV(
    filepath_CSV = "RBS.csv",
    sleep_time   = 6,
    interval     = 30
    ):

    """
    Get current transactions online. Open previously-recorded transactions, if
    any, and merge them with the current transactions to avoid duplications.
    Save the merged transactions to CSV. Do this in a loop.
    """

    while True:
        try:
            # get transactions
            print("access account")
            status = account_status(sleep_time = sleep_time)
            df = status["transactions"]
            df["balance"] = np.nan
            # add balance only to top transaction
            df.at[0, "balance"] = status["balance"]
            print("--------------------------------------------------------------------------------")
            print("current account status:\n")
            print(df)
            # check existing recorded data to avoid saving previously-saved data
            if os.path.isfile(filepath_CSV):
                #print("merge current account status with previously-recorded states")
                df_old = pd.read_csv(filepath_CSV)
                #print("--------------------------------------------------------------------------------")
                #print("previous account status:\n")
                #print(df_old)
                df = pd.concat([df_old, df], ignore_index = True).drop_duplicates().reset_index(drop = True)
                #print("--------------------------------------------------------------------------------")
                #print("merged account status:\n")
                #print(df)
                header = False
            else:
                header = True
            with open(filepath_CSV, "a") as file_CSV:
                print("save transactions to CSV {filepath}".format(filepath = filepath_CSV))
                df.to_csv(file_CSV, header = header, index = False)
        except:
            print("error accessing and recording transactions")
            pass
        print("sleep {interval} s".format(interval = interval))
        time.sleep(interval)

def payment_in_transactions_CSV(
    reference    = None,
    value        = None,
    filepath_CSV = "RBS.csv"
    ):

    """
    Access transactions recorded in CSV and load them as a DataFrame. Search
    the "description" field of the DataFrame for a specified reference. If the
    reference is found, check the value of the payment is correct by comparing
    the specified value with the "amount" field.
    """

    if not reference or not value:
        return False
    if not os.path.isfile(filepath_CSV):
        print("file {filepath} not found".format(filepath = filepath_CSV))
        sys.exit()
    df = pd.read_csv(filepath_CSV)
    match = df[df["description"].str.contains(reference)]
    if not match.empty:
        return value == match["amount"].values[0]
    else:
        return False

def printout(
    filepath_credentials = None,
    log_out              = True,
    close_driver         = True,
    sleep_time           = 20
    ):

    status = account_status(
        filepath_credentials = filepath_credentials,
        log_out              = log_out,
        close_driver         = close_driver,
        sleep_time           = sleep_time
    )
    if status:
        text = "\n\nbalance: " + str(status["balance"]) + "\n" +\
               str(status["transactions"])
    else:
        text = "error"
    return text

def find_ordinal(text):

    match = re.search(r"(^|\W)[0-9]*([04-9]?((1st|2nd|3rd|[04-9]th))|(1[1-3]th))", text)
    return None if match is None else int(match.group(0)[:-2])

def currency_string_to_float(amount):

    """
    Convert a string of the form "£2,718.28" or "-£27.18" to a float with
    appropriate sign.
    """

    try:
        value = float(decimal.Decimal(re.sub(r"[^\d.]", "", amount)))
        if amount[0] == "-":
            value = -value
        return value
    except:
        pass
    return float(0)
