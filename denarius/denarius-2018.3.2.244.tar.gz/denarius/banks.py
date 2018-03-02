# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# banks                                                                        #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides banking and other utilities.                           #
#                                                                              #
# copyright (C) 2018 William Breaden Madden, Liam Moore                        #
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

import os
import requests
import sys

import pandas as pd
import pyprel
from pymonzo import MonzoAPI

name    = "banks"
version = "2018-02-07T0053Z"

def bank_access_ok(
    bank = None
    ):
    """
    Check bank API access.
    """
    try:
        if bank == "Monzo":     df = transactions_DataFrame_Monzo()
        if bank == "RBS":       df = transactions_DataFrame_RBS()
        if bank == "Santander": df = transactions_DataFrame_Santander()
        if isinstance(df, pd.DataFrame):
            return True
        else:
            return False
    except:
        print("error -- bank access ok")
        return False

def transactions_DataFrame_Monzo(
    print_table          = False
    ):
    """
    Return a DataFrame of bank account transactions.
    """
    # API
    try:
        monzo = MonzoAPI()
        transactions = [transaction._raw_data for transaction in monzo.transactions()]
    except:
        print("error accessing Monzo API")
        return False
    # DataFrame
    df = pd.DataFrame(columns = [
        "datetime",
        "amount",
        "description",
        "notes",
        "counterparty_reference",
        "counterparty_account_number",
        "counterparty_sort_code",
        "counterparty_name",
        "currency",
        "category",
        "scheme",
        "id"
    ])
    for transaction in transactions:
        try:
            counterparty_account_number = transaction["counterparty"]["account_number"]
            counterparty_sort_code      = transaction["counterparty"]["sort_code"]
            counterparty_name           = transaction["counterparty"]["name"]
            counterparty_reference      = transaction["description"]
        except:
            counterparty_account_number = "-"
            counterparty_sort_code      = "-"
            counterparty_name           = "-"
            counterparty_reference      = "-"
        try:
            try:
                counterparty_account_number = transaction["counterparty"]["account_number"]
                counterparty_sort_code      = transaction["counterparty"]["sort_code"]
                counterparty_name           = transaction["counterparty"]["name"]
                counterparty_reference      = transaction["description"]
            except:
                counterparty_account_number = "-"
                counterparty_sort_code      = "-"
                counterparty_name           = "-"
                counterparty_reference      = "-"
            df = df.append(
                {
                    "datetime"                   : pd.to_datetime(transaction["created"]).to_pydatetime(),
                    "amount"                     : float(transaction["amount"]) / float(100),
                    "description"                : transaction["description"],
                    "notes"                      : transaction["notes"],
                    "counterparty_reference"     : counterparty_reference,
                    "counterparty_account_number": counterparty_account_number,
                    "counterparty_sort_code"     : counterparty_sort_code,
                    "counterparty_name"          : counterparty_name,
                    "currency"                   : transaction["currency"],
                    "category"                   : transaction["category"],
                    "scheme"                     : transaction["scheme"],
                    "id"                         : transaction["id"]
                },
                ignore_index = True
            )
        except:
            print("error -- transactions DataFrame Monzo")
            pass
    if print_table:
        print(table_transactions(df = df))
    return df

def transactions_DataFrame_RBS(
    filepath_credentials = "~/.rbs",
    print_table          = False
    ):
    """
    Return a DataFrame of bank account transactions.
    """
    # credentials
    filepath_credentials = os.path.expanduser(filepath_credentials)
    if not os.path.isfile(filepath_credentials):
        print("no credentials file {filepath} found".format(filepath = filepath_credentials))
        sys.exit()
    with open(filepath_credentials, "r") as file_credentials:
        credentials_string = file_credentials.read()
    credentials = {}
    exec(credentials_string, credentials)
    token        = credentials["token_teller"]
    account_code = credentials["account_code_teller"]
    # API
    try:
        URL      = "https://api.teller.io/accounts/" + account_code + "/transactions"
        headers  = {"Authorization": "Bearer " + token}
        data     = {"" : ""}
        response = requests.get(URL, json = data, headers = headers).json()
    except:
        print("error accessing Teller RBS API")
        return False
    # DataFrame
    df = pd.DataFrame(columns = ["date"])
    for transaction in response:
        df = df.append(
            {
                "date"                  : transaction["date"],
                "counterparty_reference": transaction["counterparty"],
                "description"           : transaction["description"],
                "id"                    : transaction["id"],
                "amount"                : float(transaction["amount"])
            },
            ignore_index = True
        )
    if print_table:
        print(table_transactions(df = df))
    return df

def transactions_DataFrame_bank(
    bank                 = None,
    filepath_credentials = "~/.rbs",
    print_table          = False
    ):
    try:
        if bank == "Monzo":
            return transactions_DataFrame_Monzo(
                print_table          = print_table
            )["valid"]
        elif bank == "RBS":
            return transactions_DataFrame_RBS(
                filepath_credentials = filepath_credentials,
                print_table          = print_table
            )["valid"]
        elif bank == "Santander":
            return transactions_DataFrame_Santander(
                print_table          = print_table
            )["valid"]
        else:
            return False
    except:
        print("error -- transactions DataFrame bank")
        return False

def payment_in_transactions(
    df          = None,
    reference   = None,
    amount      = None,
    print_table = False
    ):
    """
    Search the fields "counterparty_reference", "description" and "notes" (if it
    for a specified reference in a specified transactions DataFrame. If the
    reference is found, check the amount of the payment is correct by comparing
    the specified amount with the "amount" field.

    Return a dictionary of the following form:

    {
        "reference_found":   bool,      # True if reference found
        "amount_correct":    bool,      # True if sum of amounts found is amount specified
        "valid":             bool,      # True if reference found and amount correct
        "transaction"        DataFrame, # DataFrame of matches
        "amount_difference": float      # difference between amount specified and sum of amounts found
    }
    """
    reference = str(reference)
    amount    = float(amount)
    if "notes" in df.columns:
        matches = df[(df["counterparty_reference"].str.contains(reference)) | (df["description"].str.contains(reference)) | (df["notes"].str.contains(reference))]
    else:
        matches = df[(df["counterparty_reference"].str.contains(reference)) | (df["description"].str.contains(reference))]
    reference_found   = not matches.empty
    amount_correct    = sum(matches["amount"].values) == amount
    valid             = reference_found and amount_correct
    amount_difference = amount - sum(matches["amount"].values)
    transaction       = matches
    if print_table:
        print(table_transactions(df = matches))
    return {
        "reference_found":   reference_found,
        "amount_correct":    amount_correct,
        "valid":             valid,
        "amount_difference": amount_difference,
        "transactions":      matches
    }

def payment_in_transactions_Monzo(
    reference            = None,
    amount               = None,
    print_table          = False
    ):
    return payment_in_transactions(
        df          = transactions_DataFrame_Monzo(),
        reference   = reference,
        amount      = amount,
        print_table = print_table
    )

def payment_in_transactions_RBS(
    reference            = None,
    amount               = None,
    filepath_credentials = "~/.rbs",
    print_table          = False
    ):
    return payment_in_transactions(
        df          = transactions_DataFrame_RBS(filepath_credentials = filepath_credentials),
        reference   = reference,
        amount      = amount,
        print_table = print_table
    )

def payment_in_transactions_bank(
    reference            = None,
    amount               = None,
    bank                 = None,
    filepath_credentials = "~/.rbs",
    print_table          = False
    ):
    try:
        if bank == "Monzo":
            return payment_in_transactions_Monzo(
                reference            = reference,
                amount               = amount,
                print_table          = print_table
            )["valid"]
        elif bank == "RBS":
            return payment_in_transactions_RBS(
                reference            = reference,
                amount               = amount,
                filepath_credentials = filepath_credentials,
                print_table          = print_table
            )["valid"]
        elif bank == "Santander":
            return payment_in_transactions_Santander(
                reference            = reference,
                amount               = amount
            )["valid"]
        else:
            return False
    except:
        print("error -- payment in transactions bank")
        return False

def table_transactions(
    df = None
    ):
    return pyprel.Table(contents = pyprel.table_DataFrame(df = df))
