# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# Kraken                                                                       #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides Kraken utilities.                                      #
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

import time
import os
import sys

import krakenex

name    = "Kraken"
version = "2018-02-06T1826Z"

def Kraken_access_ok():
    """
    Check Kraken API access.
    """
    if last_price_XBT_EUR():
        return True
    else:
        return False

def start_API(
    filepath_credentials = "~/.kraken"
    ):
    filepath_credentials = os.path.expanduser(filepath_credentials)
    global kraken
    try:
        time.sleep(2)
        kraken = krakenex.API()
    except:
        print("Kraken API error")
    kraken.load_key(filepath_credentials)

def last_price_XBT_EUR(
    convert_value_strings_to_floats = True
    ):
    """
    Return the last price of Bitcoin in Euros.
    """
    time.sleep(2)
    try:
        request_prices_XBT_EUR = kraken.query_public("Ticker", {"pair": "XXBTZEUR"})
        if request_prices_XBT_EUR["error"] == []:
            last_price = request_prices_XBT_EUR["result"]["XXBTZEUR"]["c"][0]
            if convert_value_strings_to_floats:
                last_price = float(last_price)
            return last_price
        else:
            try:
                print(request_balances["error"][0])
            except:
                pass
            return None
    except:
        print("Kraken API error")

def balances_of_currencies(
    convert_value_strings_to_floats = True
    ):
    """
    Return the current balances of currencies held.
    """
    try:
        time.sleep(2)
        request_balances = kraken.query_private("Balance")
        if request_balances["error"] == []:
            balances = request_balances["result"]
            if convert_value_strings_to_floats:
                balances = {key: float(value) for key, value in list(balances.items())}
            return balances
        else:
            try:
                print(request_balances["error"][0])
            except:
                pass
            return None
    except:
        print("Kraken API error")
        return None

def buy_XBT_for_EUR(
    volume_in_BTC = None
    ):
    """
    Place a buy order for Bitcoin at the current market EUR price.
    """
    if isinstance(volume_in_BTC, int):
        volume_in_BTC = float(volume_in_BTC)
    if volume_in_BTC >= 0.002:
        print("place buy order for {volume} BTC at current market price".format(
            volume = volume_in_BTC
        ))
        try:
            time.sleep(2)
            request_buy = kraken.query_private(
                "AddOrder",
                {
                    "pair"            : "XXBTZEUR",
                    "type"            : "buy",
                    "ordertype"       : "market",
                    "volume"          : volume_in_BTC
                }
            )
            if request_buy["error"] == []:
                return request_buy["result"]
            else:
                try:
                    print(request_buy["error"][0])
                except:
                    pass
                return None
        except:
            print("Kraken API error")
            return None
    elif volume_in_BTC < 0.002:
        print("minimum order is 0.002 BTC")
        return None
    else:
        print("no volume specified")
        return None

def send_XBT(
    amount      = None,
    address_key = None
    ):
    """
    Send Bitcoin to an address, the key for which has been verified on Kraken.
    """
    if amount and address_key:
        print("send {amount} BTC to address key {key}".format(
            amount = amount,
            key    = address_key
        ))
        try:
            time.sleep(2)
            request_withdraw = kraken.query_private(
                "Withdraw",
                {
                    "asset" : "XBT",
                    "key"   : address_key,
                    "amount": amount
                }
            )
            if request_withdraw["error"] == []:
                return request_withdraw["result"]
            else:
                try:
                    print(request_withdraw["error"][0])
                except:
                    pass
                return None
        except:
            print("Kraken API error")
            return None
    else:
        print("no amount or no address key specified")
        return None
