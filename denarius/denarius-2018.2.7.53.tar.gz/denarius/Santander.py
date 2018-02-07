# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# Santander                                                                    #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides banking and other utilities.                           #
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

name    = "Santander"
version = "2018-01-18T1452Z"

def transactions_DataFrame(
    filepath_credentials               = "~/.santander",
    convert_currency_strings_to_floats = True,
    log_out                            = True,
    close_driver                       = True,
    sleep_time                         = 6
    ):

    """
    Access Santander online banking using credentials from a file and return
    recent transactions as a DataFrame.
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
        customer_number          = credentials["customer_number"]
        customer_PIN             = credentials["customer_PIN"]
        security_question_answer = credentials["security_question_answer"]

    # access transactions via banking website
    try:
        driver = webdriver.Firefox()
        driver.get("https://retail.santander.co.uk/LOGSUK_NS_ENS/BtoChannelDriver.ssobto?dse_operationName=LOGON")
        time.sleep(sleep_time)
        # enter customer number
        try:
            element = driver.find_element_by_name("infoLDAP_E.customerID")
            element.send_keys(customer_number)
            # login button
            button_login = driver.find_element_by_id("btnFO")
            button_login.click()
            time.sleep(sleep_time)
        except:
            pass
        ## security question
        try:
            element = driver.find_element_by_name("cbQuestionChallenge.responseUser")
            element.send_keys(security_question_answer)
            # continue button
            button_login = driver.find_element_by_name("buttons.1")
            button_login.click()
            time.sleep(sleep_time)
        except:
            pass
        # enter customer PIN
        try:
            element = driver.find_element_by_name("authentication.CustomerPIN")
            element.send_keys(customer_PIN)
            # continue button
            button_login = driver.find_element_by_name("buttons.1")
            button_login.click()
            time.sleep(sleep_time)
        except:
            pass
        # view transactions
        try:
            driver.get("https://retail.santander.co.uk/EBAN_Accounts_ENS/BtoChannelDriver.ssobto?dse_operationName=CheckForErrors&opCode=00000002&url=%2FEBAN_Accounts_ENS%2FBtoChannelDriver.ssobto%3Fdse_operationName%3DViewTransactions")
            time.sleep(sleep_time)
            # get transactions table
            transactions = driver.find_element_by_class_name("cardlytics_history_table.data")
            # convert transactions table to DataFrame
            df = pd.DataFrame(columns = ["date", "description", "money_in", "money_out", "balance"])
            for row in transactions.find_elements_by_tag_name("tr"):
                columns = row.find_elements_by_tag_name("td")
                columns = [column.text for column in columns]
                if columns:
                    df = df.append(
                        {
                            "date":        columns[0],
                            "description": columns[1],
                            "money_in":    columns[2],
                            "money_out":   columns[3],
                            "balance":     columns[4]
                        },
                        ignore_index = True
                    )
        except:
            pass
        if log_out:
            driver.get("https://retail.santander.co.uk/EBAN_Accounts_ENS/channel.ssobto?dse_operationName=contentTemplate&iurl=%2FLOGSUK_S_ENS%2Fchannel.ssobto%3Fdse_operationName%3DLOGOFF&lang=en-GB&opCode=00000098&layout=transaction")
        if close_driver:
            driver.quit()
        if convert_currency_strings_to_floats:
            df["money_in"]  = df.apply(lambda x: currency_string_to_float(x["money_in"]),  axis = 1)
            df["money_out"] = df.apply(lambda x: currency_string_to_float(x["money_out"]), axis = 1)
            df["balance"]   = df.apply(lambda x: currency_string_to_float(x["balance"]),   axis = 1)
    except:
        print("error accessing transactions")
        try:
            driver.quit()
        except:
            pass
        return None
    return df

def loop_save_transactions_to_CSV(
    filepath_CSV = "Santander.csv",
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
            df = transactions_DataFrame(sleep_time = sleep_time)
            # check existing recorded data to avoid saving previously-saved data
            if os.path.isfile(filepath_CSV):
                try:
                    df_old = pd.read_csv(filepath_CSV)
                    df = pd.concat([df_old, df], ignore_index = True).drop_duplicates().reset_index(drop = True)
                    header = False
                except:
                    print("error reading from file {filepath_CSV}".format(filepath_CSV = filepath_CSV))
                    header = True
            print(df)
            # save transactions to CSV
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
    filepath_CSV = "Santander.csv"
    ):

    """
    Access transactions recorded in CSV and load them as a DataFrame. Search
    the "description" field of the DataFrame for a specified reference. If the
    reference is found, check the value of the payment is correct by comparing
    the specified value with the "money_in" field.
    """

    if not reference or not value:
        return False
    if not os.path.isfile(filepath_CSV):
        print("file {filepath} not found".format(filepath = filepath_CSV))
        sys.exit()
    df = pd.read_csv(filepath_CSV)
    match = df[df["description"].str.contains(reference)]
    if not match.empty:
        return value == match["money_in"].values[0]
    else:
        return False

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
